from paddleocr import PPStructure
import os
import shutil
import glob
import pandas as pd
import time
import tqdm
import os.path as osp
from PIL import Image
import cv2
import numpy as np
from html2excel import ExcelParser

ppStructure = PPStructure(layout=False, show_log=True, use_gpu=True, table_model_dir='./output/SLANet/infer', gpu_id=2)
html_head = '<head>' \
            '<meta charset="UTF-8">' \
            '<style>table {border-collapse: collapse;}</style>' \
            '<style>table, th, td {border: 1px solid black;}</style>' \
            '</head>'


def detect_table_without_lines(warp_img):
    vis_img = warp_img.copy()
    result = ppStructure(warp_img)
    for region in result:
        if region['type'] == 'table':
            html = region['res']['html'].replace("<html>", f"<html>{html_head}")
            cell_bbox = region['res']['boxes']
            x, y = region['bbox'][0], region['bbox'][1]
            for cell in cell_bbox:
                pt1, pt2 = (int(x + cell[0]), int(y + cell[1])), (int(x + cell[2]), int(y + cell[3]))
                cv2.rectangle(vis_img, pt1, pt2, (255, 0, 0), 2)
            return html, vis_img
    return "", warp_img

def save_ret(name, html):
    html_path = f'{name}.html'
    with open(html_path, 'w') as f:
        f.write(html)
    if html != "":
        parser = ExcelParser(html_path)
        parser.to_excel(f"{name}.xlsx")

if __name__ == '__main__':
    save_folder = "/home/zjlab/lwm/result/tablebank_new/"
    if os.path.exists(save_folder):
        shutil.rmtree(save_folder)
    os.makedirs(save_folder)

    paths = glob.glob('/home/zjlab/lwm/dataset/TableBank/images/*/*')
    valid_paths = []
    df = pd.read_excel("/home/zjlab/lwm/dataset/TableBank/tablebank_line_true.xlsx")
    valid_paths = df.values[:, 0]

    num_file = 0
    start = time.time()
    for img_path in tqdm.tqdm(paths):
        if not os.path.split(img_path)[1] in valid_paths:
            continue
        num_file += 1
        subfolder, filename = img_path.split("/")[-2:]
        save_subfolder = save_folder + subfolder + "/"
        if not os.path.exists(save_subfolder):
            os.makedirs(save_subfolder)
        save_path = save_subfolder + osp.splitext(filename)[0]
        if os.path.exists(save_path + ".html") or os.path.exists(save_path + "_line.html"):
            print("file exist")
            continue
        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        img = img.resize((w * 2, h * 2))
        try:
            html, vis_img = detect_table_without_lines(np.asarray(img))
            save_ret(save_path, html)
        except Exception as e:
            print(f"Exception: {e}!!!")
            save_ret(save_path + "_fail", "")
    total_time = time.time() - start
    avg_time = total_time / num_file
    print(f"all time: {total_time}")
    print(f"average time: {total_time}/{num_file}={avg_time}")
    with open("log.txt", "w") as f:
        f.write(str(avg_time))
