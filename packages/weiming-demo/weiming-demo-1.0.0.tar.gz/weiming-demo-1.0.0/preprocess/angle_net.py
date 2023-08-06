#!/usr/bin/env python
# -*- coding: utf-8 -*-
# _Author_: xiaofeng
# Date: 2018-04-22 18:13:46
# Last Modified by: xiaofeng
# Last Modified time: 2018-04-22 18:13:46
'''
根据给定的图形，分析文字的朝向
'''
# from keras.models import load_model
import numpy as np
from PIL import Image
from keras.applications.vgg16 import preprocess_input, VGG16
from keras.layers import Dense
from keras.models import Model
# 编译模型，以较小的学习参数进行训练
from keras.optimizers import SGD
import os
cur_dir = os.path.dirname(os.path.abspath(__file__))


class AngleNetHandle():
    def __init__(self):
        vgg = VGG16(weights=None, input_shape=(224, 224, 3))
        # 修改输出层 3个输出
        x = vgg.layers[-2].output
        predictions_class = Dense(
            4, activation='softmax', name='predictions_class')(x)
        prediction = [predictions_class]
        model = Model(inputs=vgg.input, outputs=prediction)
        sgd = SGD(lr=0.00001, momentum=0.9)
        model.compile(
            optimizer=sgd, loss='categorical_crossentropy', metrics=['accuracy'])
        model.load_weights(
            f'{cur_dir}/weights/modelAngle.h5')
        self.model = model

    def predict(self, im):
        """
        图片文字方向预测
        """
        ROTATE = [0, 90, 180, 270]
        w, h = im.size
        # 对图像进行剪裁
        # 左上角(int(0.1 * w), int(0.1 * h))
        # 右下角(w - int(0.1 * w), h - int(0.1 * h))
        xmin, ymin, xmax, ymax = int(0.1 * w), int(
            0.1 * h), w - int(0.1 * w), h - int(0.1 * h)
        im = im.crop((xmin, ymin, xmax, ymax))  # 剪切图片边缘，清除边缘噪声
        # 对图片进行剪裁之后进行resize成(224,224)
        im = im.resize((224, 224))
        # 将图像转化成数组形式
        img = np.array(im)
        img = preprocess_input(img.astype(np.float32))
        pred = self.model.predict(np.array([img]))
        index = np.argmax(pred, axis=1)[0]
        return ROTATE[index]
