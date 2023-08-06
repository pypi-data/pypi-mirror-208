import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance, ImageFont, ImageDraw, ImageFilter
import numpy as np
import re
import os.path as osp
from table_ocr import preprocess_image, TableOCR
import os
import glob
from PaddleOCR.paddleocr import PPStructure, draw_structure_result, save_structure_res

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号 #有中文出现的情况，需要u'内容'

structure_engine = PPStructure(show_log=False, image_orientation=False, table=False, use_gpu=True,
                               lang='ch', layout_score_threshold=0.5, layout_model_dir='PaddleDetection/output_inference/picodet_lcnet_x1_0_layout_cdla')
table_ocr = TableOCR(save_result=False)


def detect_chapter(txt):
    p = re.compile("^(\*|-)?(第.{1,2}章|\d{1,2})")
    ret = p.search(txt)
    if ret is not None:
        return True
    else:
        return False


def detect_section(txt):
    p = re.compile("^(\*|\$|-)?(\d{1,2}(\.|-|·)\d{1,2})")
    ret = p.search(txt)
    if ret is not None:
        return True
    else:
        return False


def detect_point(txt):
    p = re.compile("^(\*|-)?(\d{1,2}\.\d{1,2}\.\d{1,2})")
    ret = p.search(txt)
    if ret is not None:
        return True
    else:
        return False


def detect_subpoint(txt):
    p = re.compile("^(\*|-)?(\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2})")
    ret = p.search(txt)
    if ret is not None:
        return True
    else:
        return False


def text_postprocess(txt):
    txt = re.sub("-|—|－", "-", txt)
    txt = txt.replace("..", ".").replace("、", ".").replace(",", ".").replace("l", "1").replace("I", "1")
    txt = re.sub(" |　", "", txt)
    return txt


def run(img_path):
    folder = osp.split(osp.split(img_path)[0])[1]
    filename = os.path.basename(img_path).split('.')[0]
    save_folder = "/tmp/algo/" + osp.split(folder)[1]
    if not osp.exists(save_folder):
        os.makedirs(save_folder)

    img = Image.open(img_path)
    img = preprocess_image(img, False)
    img = np.asarray(img)
    result = structure_engine(img)

    for region in result:
        type = region['type']
        for res in region['res']:
            res['label'] = type
            if type in ['text', 'title']:
                txt = res['text']
                post_txt = text_postprocess(txt)
                if detect_point(post_txt) or detect_subpoint(post_txt):
                    res['label'] = 'text'
                elif detect_section(post_txt) or detect_chapter(post_txt) and type == 'title':
                    res['label'] = 'title'
        if type == 'table':
            html = table_ocr(region['img'], f'{save_folder}/{filename}')[0]
            region['res']['html'] = html

    save_structure_res(result, save_folder, filename)

    font_path = 'simfang.ttf'  # PaddleOCR下提供字体包
    img = draw_structure_result(img, result, font_path=font_path)
    img.save(f'{save_folder}/{filename}/{filename}.jpg')


def run_all(folder):
    for img_path in glob.glob(folder + "/*/*.png"):
        print(img_path)
        run(img_path)


if __name__ == '__main__':
    folder = "/home/igor/zjlab/标准化项目/标准文本示例"
    # img_path = "/home/igor/zjlab/标准化项目/标准文本示例/GB 1589-2016 汽车、挂车及汽车列车外廓尺寸、轴荷及质量限值/10.png"
    # img_path = "/home/igor/zjlab/标准化项目/标准文本示例/GB 1589-2016 汽车、挂车及汽车列车外廓尺寸、轴荷及质量限值/09.png"
    img_path = "/home/igor/zjlab/标准化项目/标准文本示例/GB∕T 40728-2021 再制造 机械产品修复层质量检测方法/01.png"
    # img_path = '/home/igor/zjlab/智慧教育/pix2seq/01.png'
    run(img_path)
    # run_all(folder)
