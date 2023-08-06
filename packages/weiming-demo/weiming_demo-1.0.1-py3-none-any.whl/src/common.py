import math
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import glob
import os
import os.path as osp
from pdf2image import convert_from_path, convert_from_bytes
from io import BytesIO
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


class DamoOCR():
    def __int__(self):
        pass

    def ocr(self, img):
        ocr_detection = pipeline(Tasks.ocr_detection, model='damo/cv_resnet18_ocr-detection-line-level_damo')
        ocr_recognition = pipeline(Tasks.ocr_recognition, model='damo/cv_convnextTiny_ocr-recognition-document_damo')
        lines = ocr_detection(img)['polygons'].astype(int)
        info = []
        for line in lines:
            line = line.reshape([4, 2])
            x1, y1, x2, y2 = min(line[:, 0]), min(line[:, 1]), max(line[:, 0]), max(line[:, 1])
            ocr_img = img[y1:y2, x1:x2]
            txt = ocr_recognition(ocr_img)['text']

            pos = txt[1]
            width = x2 - x1
            pos = pos * width + x1
            pos = np.round(pos).astype(int)
            pos = pos.tolist()
            info.append([[[x1, y1], [x2, y1], [x2, y2], [x1, y2]], [txt[0], 1, pos]])
        return info


def pdf2png(pdf, save_folder):
    if osp.exists(save_folder):
        shutil.rmtree(save_folder)
    os.makedirs(save_folder)

    if type(pdf) == str:
        convert_from_path(
            pdf_path=pdf,  # 要转换的pdf的路径
            dpi=200,  # dpi中的图像质量（默认200）
            output_folder=save_folder,  # 将生成的图像写入文件夹（而不是直接写入内存）#注意中文名的目录可能会出问题
            first_page=None,  # 要处理的第一页
            last_page=None,  # 停止前要处理的最后一页
            fmt="png",  # 输出图像格式
            jpegopt=None,  # jpeg选项“quality”、“progressive”和“optimize”（仅适用于jpeg格式）
            thread_count=32,  # 允许生成多少线程进行处理
            userpw=None,  # PDF密码
            use_cropbox=False,  # 使用cropbox而不是mediabox
            strict=False,  # 当抛出语法错误时，它将作为异常引发
            transparent=False,  # 以透明背景而不是白色背景输出。
            single_file=False,  # 使用pdftoppm/pdftocairo中的-singlefile选项
            poppler_path=None,  # 查找poppler二进制文件的路径
            grayscale=False,  # 输出灰度图像
            size=None,  # 结果图像的大小，使用枕头（宽度、高度）标准
            paths_only=False,  # 不加载图像，而是返回路径（需要output_文件夹）
            use_pdftocairo=False,  # 用pdftocairo而不是pdftoppm，可能有助于提高性能
            timeout=None,  # 超时
        )
    else:
        convert_from_bytes(
            pdf_file=pdf,  # 要转换的pdf的路径
            dpi=200,  # dpi中的图像质量（默认200）
            output_folder=save_folder,  # 将生成的图像写入文件夹（而不是直接写入内存）#注意中文名的目录可能会出问题
            first_page=None,  # 要处理的第一页
            last_page=None,  # 停止前要处理的最后一页
            fmt="png",  # 输出图像格式
            jpegopt=None,  # jpeg选项“quality”、“progressive”和“optimize”（仅适用于jpeg格式）
            thread_count=32,  # 允许生成多少线程进行处理
            userpw=None,  # PDF密码
            use_cropbox=False,  # 使用cropbox而不是mediabox
            strict=False,  # 当抛出语法错误时，它将作为异常引发
            transparent=False,  # 以透明背景而不是白色背景输出。
            single_file=False,  # 使用pdftoppm/pdftocairo中的-singlefile选项
            poppler_path=None,  # 查找poppler二进制文件的路径
            grayscale=False,  # 输出灰度图像
            size=None,  # 结果图像的大小，使用枕头（宽度、高度）标准
            paths_only=False,  # 不加载图像，而是返回路径（需要output_文件夹）
            use_pdftocairo=False,  # 用pdftocairo而不是pdftoppm，可能有助于提高性能
            timeout=None,  # 超时
        )

    for path in glob.glob(save_folder + "/*.png"):
        new_path = f"{save_folder}/{path.split('-')[-1]}"
        os.renames(path, new_path)


def detect_text_lines(img, ppocr, save_folder=None):
    result = ppocr.ocr(img)
    if len(result) == 0:
        return [], [], [], 0

    txts = []
    boxes = []
    txt_regions = []
    for info in result:
        txts.append(info[1][0])
        boxes.append((info[0][0][0], info[0][0][1], info[0][1][0], info[0][2][1]))
        txt_regions.append(info[1][2])
    ys = np.array([box[1] for box in boxes])
    diff_ys = ys[1:] - ys[:-1]
    font_size = np.median((diff_ys[diff_ys > 5])) / 2
    if math.isnan(font_size):
        font_size = boxes[0][3] - boxes[0][1]

    if save_folder:
        vis_img = Image.fromarray(img)
        draw_img = ImageDraw.Draw(vis_img)
        font_size2 = int(font_size/2)
        font = ImageFont.truetype("/home/zjlab/algo/Table-OCR/simfang.ttf", font_size2, encoding="utf-8")
        for txt, box in zip(txts, boxes):
            draw_img.rectangle(box, outline='red', width=3)
            draw_img.text((box[0], box[1] - font_size2), txt, fill='blue', font=font)
        vis_img.save(f'{save_folder}/ocr.png')
    return txts, boxes, txt_regions, font_size


def ocr(path, file=None, is_streamlit=False, save_pages=False):
    if is_streamlit:
        import streamlit as st
    from PaddleOCR.paddleocr import PaddleOCR
    PPOCR = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, use_gpu=True)
    # PPOCR = DamoOCR()

    basename, ext = osp.splitext(path)
    if ext == ".pdf":
        if file != None:
            pdf2png(file, basename)
        else:
            pdf2png(path, basename)
        all_txts = []
        paths = glob.glob(basename + "/*.png")
        paths.sort()
        for img_path in paths:
            img = np.array(Image.open(img_path).convert('RGB'))
            if is_streamlit and len(paths) < 5:
                st.image(img, caption="Input", use_column_width=True)
            txts, boxes, txt_regions, font_size = detect_text_lines(img, PPOCR)
            if save_pages:
                save_path = img_path.replace(".png", ".txt")
                with open(save_path, "w") as f:
                    f.write(txts)
            all_txts += txts
        all_txts = "\n".join(all_txts)
        save_path = basename + ".txt"
        with open(save_path, "w") as f:
            f.write(all_txts)
    else:
        if file != None:
            img = np.array(Image.open(BytesIO(file)).convert('RGB'))
        else:
            img = np.array(Image.open(path).convert('RGB'))
        if is_streamlit:
            st.image(img, caption="Input", use_column_width=True)
        txts, boxes, txt_regions, font_size = detect_text_lines(img, PPOCR)
        all_txts = "\n".join(txts)
        save_path = path.replace(".png", ".txt")
        with open(save_path, "w") as f:
            f.write(all_txts)
    return all_txts


if __name__ == '__main__':
    # for path in glob.glob("/home/igor/zjlab/标准化项目/爱仕达/GBT 2828.1-2012 计数抽样检验程序 第1部分：按接收质量限（AQL）检索的逐批检验抽样计划.pdf"):
    #     # ocr(path)
    #     save_folder = osp.splitext(path)[0]
    #     pdf2png(save_folder, path)

    # img = Image.open('../data/test/test.png')
    # W, H = img.size
    # h = 1000
    # count = math.ceil(H / h)
    # for i in range(count):
    #     roi = img.crop((0, h * i, W, min(H, h * (i + 1))))
    #     save_path = f'../data/test/{i}.png'
    #     roi.save(save_path)
    #     ocr(save_path)
    #
    # txts = []
    # for i in range(count):
    #     with open(f'../data/test/{i}.txt', 'rb') as f:
    #         txts += f.readlines()
    # with open(f'../data/test/result.txt', 'wb') as f:
    #     f.writelines(txts)

    # from PaddleOCR.paddleocr import PaddleOCR
    # PPOCR = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, use_gpu=True)
    # # PPOCR = DamoOCR()
    # img = Image.open('/home/zjlab/algo/Table-OCR/education/data/B15_【机械工业】机器人学导论/275.png')
    # # new_img = Image.new('RGB', (500,36), (255,255,255))
    # # new_img.paste(img)
    # txts = detect_text_lines(np.array(img), PPOCR)[0]
    # print('\n'.join(txts))

    ocr('data/GB∕T 26610.1-2022 承压设备系统基于风险的检验实施导则 第1部分：基本要求和实施程序.pdf', save_pages=True)