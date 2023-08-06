import os
import shutil
import time
import numpy as np
from PIL import Image
import os.path as osp
import xml.etree.ElementTree as ET
from tqdm import tqdm
import sys

sys.path.append('/home/zjlab/algo/Table-OCR/LatexOCR')

from common import detect_text_lines
from PaddleOCR.paddleocr import PaddleOCR
from table_ocr import TableOCR
from DINO.predict import DinoDetector, compute_iou
from LatexOCR.predict import FormulaRecognizer
from LatexOCR.formula2png import build_images


def preprocess(img):
    return np.uint8(img / np.max(img) * 255)


def detect(save_result=False):
    formula_recognizer = FormulaRecognizer('/home/zjlab/algo/Table-OCR/LatexOCR/pix2tex/model/settings/config.yaml',
                                           '/home/zjlab/algo/Table-OCR/LatexOCR/checkpoints/^pix2tex/best.pth')
    PPOCR = PaddleOCR(use_angle_cls=False, lang="ch", show_log=False, merge_row=True, use_gpu=True)
    table_ocr = TableOCR()
    layout_detector = DinoDetector('book', 'book', f"/home/zjlab/algo/Table-OCR/DINO/config/DINO/DINO_4scale.py",
                                   save_result=save_result, save_roi=False)
    formula_detector = DinoDetector('ibem', 'ibem+formula',
                                    f"/home/zjlab/algo/Table-OCR/DINO/config/DINO/DINO_4scale_formula.py",
                                    save_result=save_result, save_roi=False)

    start_time = time.time()
    bookname = 'B6_7-8'
    filename = '011'
    img_path = f'/home/zjlab/algo/dataset/education/{bookname}/{filename}.png'
    save_folder = f'result/{bookname}/{filename}'
    if osp.exists(save_folder):
        shutil.rmtree(save_folder)
    os.makedirs(save_folder)

    img = Image.open(img_path).convert('RGB')
    np_img = np.array(img)
    np_img = preprocess(np_img)
    w, h = img.size

    print('detect layout...')
    layouts = layout_detector.detect(img_path)[0]
    layouts = sorted(layouts, key=lambda x: (x[0][1], x[0][0]))

    print('detect formula...')
    formulas = formula_detector.detect(img_path)[0]
    formulas = sorted(formulas, key=lambda x: (x[0][1], x[0][0]))

    print('recognize formula...')
    fboxes = []
    fs = []
    save_paths = []
    formula_time = time.time()
    for i, (box, label, score) in enumerate(formulas):
        x1, y1, x2, y2 = round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)
        np_img[y1:y2, x1:x2] = (255, 255, 255)
        box = (x1, y1, x2, y2)
        object_img = img.crop(box)
        if save_result:
            object_img.save(f'{save_folder}/{i}_true.png')
            save_paths.append(f'{i}_pred.png')
        fboxes.append(box)
        f = formula_recognizer.detect(object_img)
        fs.append(f)
    print(f'formula time: {(time.time()-formula_time)/len(fs)}')
    if save_result:
        build_images(fs, save_paths, save_folder)

    for i, (box, label, score) in tqdm(enumerate(layouts)):
        x1, y1, x2, y2 = round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)
        if label in ['Figure', 'Table']:
            np_img[y1:y2, x1:x2] = (255, 255, 255)

        # merge layout of formula and text
        if i > 0 and label in ['Formula', 'Text']:
            if layouts[i - 1][1] in ['Formula', 'Text']:
                merge_boxes = np.array([layouts[i - 1][0], [x1, y1, x2, y2]]).reshape((2, 4))
                x1, y1, x2, y2 = np.min(merge_boxes[:, 0]), np.min(merge_boxes[:, 1]), np.max(
                    merge_boxes[:, 2]), np.max(merge_boxes[:, 3])
                layouts[i - 1] = None
            layouts[i][1] = 'Text'
        layouts[i][0] = [x1, y1, x2, y2]

    print('ocr...')
    txts, boxes, txt_regions, font_size = detect_text_lines(np_img, PPOCR, save_folder=save_folder)
    txts = [list(txt) for txt in txts]

    for fbox, f in zip(fboxes, fs):
        dists = [abs(fbox[1] - tbox[1]) for tbox in boxes]
        min_dist = min(dists)
        if min_dist < font_size:
            label = 'embedded'
            f = f'${f}$'
        else:
            label = 'isolated'
            f = f'$${f}$$'
            dists = [abs(fbox[1] - tbox[3]) for tbox in boxes]
        yid = np.argmin(dists)

        if label == 'embedded':
            chars = txts[yid]
            cboxes = txt_regions[yid]
            dists = []
            for char, cbox in zip(chars, cboxes):
                dist = abs(fbox[0] - cbox[2])
                dists.append(dist)
            xid = np.argmin(dists) + 1
            chars.insert(xid, f)
            cboxes.insert(xid, fbox)
            txts[yid] = chars
            txt_regions[yid] = cboxes
        else:
            boxes.insert(yid + 1, fbox)
            txts.insert(yid + 1, [f])
            txt_regions.insert(yid + 1, [fbox])

    txts = [''.join(txt) for txt in txts]

    root_xml = ET.Element('root')
    for i in range(len(layouts)):
        if layouts[i] is None:
            continue
        box, label, score = layouts[i]
        child_xml = ET.SubElement(root_xml, label)
        object_img = img.crop(box)
        if label == 'Figure':
            save_path = f'{save_folder}/{label}_{i}.png'
            print(save_path)
            object_img.save(save_path)
            child_xml.text = save_path
        elif label == 'Table':
            html, json_ret, vis_img, warp_img, warp_mask, cells = table_ocr(object_img, f'{save_folder}/{label}_{i}')
            child_xml.text = html
        else:
            match_txts = []
            for t, b in zip(txts, boxes):
                if compute_iou(box, b) > 0:
                    match_txts.append(t)
            txt = '\\\\ '.join(match_txts).replace('$$\\\\ ', '$$')
            child_xml.text = txt
    tree = ET.ElementTree(root_xml)
    tree.write(f'{save_folder}/result.xml', encoding='utf-8')
    print(f'save result to {save_folder}')
    print(f'total time: {time.time()-start_time}')


if __name__ == '__main__':
    detect(save_result=True)
