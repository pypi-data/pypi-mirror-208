import json
import glob
import os
import shutil
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial import KDTree
from PIL import Image, ImageEnhance, ImageFont, ImageDraw, ImageFilter
# from table_detector.table import get_table_ceilboxes, draw_lines
from hough_lines import get_table_ceilboxes, draw_lines
import cv2
import numpy as np
import re
from shapely.geometry import Polygon
from sklearn.cluster import DBSCAN
import os.path as osp
import math
import time
import tqdm
from PaddleOCR.paddleocr import PPStructure
from PaddleOCR.paddleocr import PaddleOCR
from html2excel import ExcelParser
from common import detect_text_lines, pdf2png, DamoOCR
from scipy.optimize import linear_sum_assignment

# from preprocess import edsr
# from crnn_handwriting.crnn_torch import crnnOcr
# sr_model = edsr.build_model(scale=4, num_res_blocks=16)
# sr_model.load_weights('weights/edsr-16-x4.h5')

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号 #有中文出现的情况，需要u'内容'

html_head = '<head>' \
            '<meta charset="UTF-8">' \
            '<style>table {border-collapse: collapse;}</style>' \
            '<style>table, th, td {border: 1px solid black;}</style>' \
            '</head>'

globals = {
    'nan': ""
}


class NpEncoder(json.JSONEncoder):
    """Convert numpy classes to JSON serializable objects."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def show_image(src, window_name="img", wait=0, debug=True, destroy=True):
    if debug:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1600, 900)
        cv2.imshow(window_name, np.asarray(src))
        cv2.waitKey(wait)
        if destroy:
            cv2.destroyWindow(window_name)


class TableOCR:
    def __init__(self, angle=True, use_pp=False, save_result=True, kie=False, lang="ch"):
        print("App started!")
        self.angle = angle
        self.use_pp = use_pp
        self.save_result = save_result
        self.kie = kie
        self.PPOCR = PaddleOCR(use_angle_cls=False, lang=lang, show_log=False, use_gpu=True)
        # self.PPOCR = DamoOCR()
        self.PPTABLE = PPStructure(layout=False, lang=lang, show_log=False, use_gpu=True, table_max_len=488)

    def __call__(self, img, ori_name, preprocess=True, is_streamlit=False, full_img=False, template=None):
        if type(img) == np.ndarray:
            img = Image.fromarray(img)
        w, h = img.size
        nw = min(2000, w)
        if nw != w:
            nh = int(nw / w * h)
            img = img.resize((nw, nh))
        if osp.exists(ori_name):
            shutil.rmtree(ori_name)
        os.makedirs(ori_name)
        name = f"{ori_name}/result"
        if self.kie:
            return self.run_kie(img, name, preprocess, is_streamlit, full_img, template)
        else:
            return self.run_table(img, name, preprocess, is_streamlit, self.save_result)

    def run_table(self, img, name, preprocess, is_streamlit, save_result):
        json_ret = {}
        if preprocess:
            img = preprocess_image(img, self.angle)
            img = binary(img)
        if self.use_pp:
            html, vis_img = self.detect_table_without_lines(np.asarray(img))
            if save_result: save_ret(name, html, json_ret, vis_img)
            return html, json_ret, vis_img, img, None, []
        else:
            warp_img, warp_mask, cells = extract_table(img)
            if warp_img is None or len(cells) < 2:
                print("no table found")
                warp_img = np.asarray(img)
                html, vis_img = self.detect_table_without_lines(warp_img)
            else:
                if not is_streamlit:
                    name += "_line"
                if is_streamlit:
                    import streamlit as st
                    line_img = warp_img.copy()
                    for pt1, pt2 in cells:
                        line_img = cv2.rectangle(line_img, pt1, pt2, (255, 0, 0), 2)
                    st.image(warp_mask, caption='mask', use_column_width=True)
                    st.image(line_img, caption='Detected lines', use_column_width=True)

                start = time.time()
                html, json_ret, vis_img = self.detect_text(warp_img, cells)
                end = time.time()
                print(f"detect_text: {end - start}")
            if save_result: save_ret(name, html, json_ret, vis_img)
            return html, json_ret, vis_img, warp_img, warp_mask, cells

    def run_kie(self, img, name, preprocess, is_streamlit, full_img, template):
        json_ret = {}
        html = ""
        if preprocess:
            img = preprocess_image(img, self.angle)
        warp_img, warp_mask, cells = extract_table(img)
        Image.fromarray(warp_img).save(name+'_warp_img.png')
        Image.fromarray(warp_mask).save(name + '_warp_mask.png')
        if full_img:
            warp_img = np.array(img)
        h, w = warp_img.shape[:2]
        vis_img = warp_img.copy()
        if template is None:
            template = find_template(cells, w, h)
        kvs = template["kvs"]
        actions = template["actions"]
        vis_img = draw_actions(vis_img, kvs, actions)
        if template is not None:
            if is_streamlit:
                import streamlit as st
                st.image(vis_img, caption='Found template', use_column_width=True)
            kvs = template["kvs"]
            actions = template["actions"]
            if "keys" in template:
                keys = template["keys"]
            key_id = 0
            dict_str = ""
            i = 0
            count = 0
            for k, action in enumerate(actions):
                if action in ["a", "s", "d", "f", "k"]:
                    x0, y0, x1, y1 = kvs[i]
                    roi_img = warp_img[y0:y1, x0:x1]
                    if action == 'a':
                        txts, boxes, txt_regions, font_size = detect_text_lines(roi_img, self.PPOCR)
                        txt = "".join(txts).replace('"', '\\"')
                        dict_str += f'"{txt}":'
                        i += 1
                    elif action == 's':
                        txts, boxes, txt_regions, font_size = detect_text_lines(roi_img, self.PPOCR)
                        txt = "\t".join(txts).replace('"', '\\"')
                        if k == 0 or actions[k - 1] not in ['a', 'k']:
                            dict_str += '"text":'
                        dict_str += f'"{txt}",'
                        i += 1
                    elif action == 'd':
                        html = self.run_table(Image.fromarray(roi_img), f"{name}_{count}", preprocess=preprocess,
                                              is_streamlit=is_streamlit, save_result=True)[0]
                        tmp_list = html_to_list(html)
                        if k == 0 or actions[k - 1] != 'a':
                            dict_str += '"table":'
                        dict_str += f"{tmp_list},"
                        i += 1
                        count += 1
                    elif action == 'f':
                        figure_img = Image.fromarray(roi_img)
                        figure_path = f"{name}_{count}.png"
                        figure_img.save(figure_path)
                        if k == 0 or actions[k - 1] != 'a':
                            dict_str += '"image":'
                        dict_str += f"'{figure_path}',"
                        i += 1
                        count += 1
                    elif action == 'k':
                        dict_str += f'"{keys[key_id]}":'
                        key_id += 1
                    # for box, txt_region in zip(boxes, txt_regions):
                    #     x2, y2, x3, y3 = int(box[0][0]), int(box[0][1]), int(box[2][0]), int(box[2][1])
                    #     for xl, xr in txt_region:
                    #         cv2.rectangle(tmp_img, (x0+xl, y0+y2), (x0+xr, y0+y3), (0, 255, 0), 2)
                else:
                    if action == 'q':
                        dict_str += "{"
                    elif action == 'w':
                        dict_str += "},"
                    elif action == 'e':
                        if k == 0 or actions[k - 1] != 'a':
                            dict_str += '"list":'
                        dict_str += "["
                    elif action == 'r':
                        dict_str += "],"
            json_ret = eval("{" + dict_str + "}", globals)
            if self.save_result: save_ret(name, html, json_ret, vis_img)
            # show_image(tmp_img)
        return html, json_ret, vis_img, warp_img, warp_mask, cells

    def detect_table_without_lines(self, warp_img):
        vis_img = warp_img.copy()
        text_img = Image.fromarray(np.zeros_like(vis_img, np.uint8) + 255)
        canvas = ImageDraw.Draw(text_img)
        result = self.PPTABLE(warp_img)
        for region in result:
            if region['type'] == 'table':
                html = region['res']['html'].replace("<html>", f"<html>{html_head}")
                boxes = region['res']['boxes']
                texts = region['res']['rec_res']
                x, y = region['bbox'][0], region['bbox'][1]
                for x0, y0, _, _, x1, y1, _, _ in region['res']['cell_bbox']:
                    pt1, pt2 = (int(x + x0), int(y + y0)), (int(x + x1), int(y + y1))
                    cv2.rectangle(vis_img, pt1, pt2, (255, 0, 0), 2)
                for (x0, y0, x1, y1), (text, score, text_region) in zip(boxes, texts):
                    pt1, pt2 = (int(x + x0), int(y + y0)), (int(x + x1), int(y + y1))
                    cv2.rectangle(vis_img, pt1, pt2, (0, 0, 255), 2)
                    font_size = int((y1 - y0) * 0.7)
                    font = ImageFont.truetype('simfang.ttf', font_size, encoding="utf-8")
                    canvas.text(pt1, text, (0, 0, 0), font=font)
                text_img = np.asarray(text_img)
                vis_img = np.vstack((vis_img, text_img))
                return html, vis_img
        return "", warp_img

    def detect_text(self, warp_img, cells):
        vis_img = warp_img.copy()
        text_img = Image.fromarray(np.zeros_like(vis_img, np.uint8) + 255)
        canvas = ImageDraw.Draw(text_img)
        char_info = []
        font_sizes = []
        json_ret = {}
        font_size_ratio = 0.7

        result = self.PPTABLE(warp_img)
        for region in result:
            if region['type'] == 'table':
                boxes = region['res']['boxes']
                texts = region['res']['rec_res']
                x, y = region['bbox'][0], region['bbox'][1]
                for (x0, y0, x1, y1), (text, score, text_region) in zip(boxes, texts):
                    char_info.append([[(x0 + x1) / 2 + x, (y0 + y1) / 2 + y], text])
                    font_size = int((y1 - y0) * font_size_ratio)
                    font_sizes.append(font_size)
                    # pt1, pt2 = (int(x + x0), int(y + y0)), (int(x + x1), int(y + y1))
                    # cv2.rectangle(vis_img, pt1, pt2, (0, 0, 255), 2)
                    # font = ImageFont.truetype('simfang.ttf', font_size, encoding="utf-8")
                    # canvas.text(pt1, text, (0, 0, 0), font=font)
        if len(char_info) == 0:
            return "", json_ret, vis_img

        start = time.time()
        char_info = sorted(char_info, key=lambda x: (x[0][1], x[0][0]))
        char_info = np.asarray(char_info)
        font_size = np.median(font_sizes)
        col_height = int(np.median([y1 - y0 for (x0, y0), (x1, y1) in cells]))
        print(f"font size: {font_size}, col height: {col_height}")

        df, rowspan_array, colspan_array = merge_cells(cells, char_info, font_size)
        html = df_to_html(df, rowspan_array, colspan_array)
        print(df)
        text_img = np.asarray(text_img)
        vis_img = np.vstack((vis_img, text_img))

        end = time.time()
        print(f"postprocess: {end - start}")
        return html, json_ret, vis_img

    def manual_template(self, warp_img, name, cells):
        from draw_template import draw_template_kv
        print("draw template now")

        vis_img = None
        html = ""
        json_ret = {}
        kvs, actions, keys = draw_template_kv(warp_img, cells)
        template = save_template(warp_img, cells, kvs, actions, keys)
        if template is not None:
            html, json_ret, vis_img = self.detect_text(warp_img, cells)
        save_ret(name, html, json_ret, vis_img)
        return html, json_ret, vis_img

    def fill_lines(self, warp_img, name, warp_mask):
        from draw_line import manual_draw_line
        print("draw lines now")

        line_img = warp_img.copy()
        line_img[np.where(warp_mask > 0)] = (255, 0, 0)
        manual_lines = manual_draw_line(line_img)

        warp_mask = draw_lines(warp_mask, manual_lines, color=255, lineW=1)
        cnts, _ = cv2.findContours(warp_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[1:]
        rects = [cv2.boundingRect(cnt) for cnt in cnts]
        new_cells = [[(x, y), (x + w, y + h)] for x, y, w, h in rects]

        html, json_ret, vis_img = self.detect_text(warp_img, new_cells)
        save_ret(name, html, json_ret, vis_img)
        return html, vis_img, new_cells


def save_ret(name, html, json_ret, vis_img):
    print("save path: " + name)
    html_path = f'{name}.html'
    if html != "":
        with open(html_path, 'w') as f:
            f.write(html)
        parser = ExcelParser(html_path)
        parser.to_excel(f"{name}.xlsx")
    if json_ret != {}:
        with open(f"{name}.json", "w") as f:
            json.dump(json_ret, f, ensure_ascii=False, cls=NpEncoder)
    Image.fromarray(vis_img).save(f"{name}.png")


def preprocess_image(img, angle=True):
    if angle:
        from preprocess.angle_net import AngleNetHandle
        angle_detector = AngleNetHandle()
        angle = angle_detector.predict(img)
        if 0 < angle < 180:
            print(f"rotate img {-angle} degree")
            img = img.rotate(-angle, expand=True)

    img = scale(img)
    img = contrast(img, 1.5)
    # img = padding(img, 10)
    return img


def resize(img):
    w, h = img.size
    return img.resize((2 * w, 2 * h))


def binary(img):
    return img.convert("L").convert("RGB")
    # img_np = np.array(img.convert("L"))
    # img_np = 255 - cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 5)
    # return Image.fromarray(img_np).convert("RGB")


def padding(img, pad):
    if type(img) == np.ndarray:
        h, w = img.shape[:2]
        p = np.zeros((h + pad * 2, w + pad * 2, 3), np.uint8) + 255
        p[pad:pad + h, pad:pad + w] = img
    else:
        w, h = img.size
        p = Image.new('RGB', (w + pad * 2, h + pad * 2), (255, 255, 255))
        blank = Image.new('RGB', (w + 2, h + 2), (0, 0, 0))
        p.paste(blank, (pad - 1, pad - 1, w + pad + 1, h + pad + 1))
        p.paste(img, (pad, pad, w + pad, h + pad))
    return p


def draw_actions(raw_img, kvs, actions):
    img = raw_img.copy()
    i = 0
    for action in actions:
        if action in ["a", "s", "d", "f"]:
            x0, y0, x1, y1 = kvs[i]
            if action == "a":  # save key region
                cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 0), thickness=2)
            elif action == "s":  # save value region
                cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), thickness=2)
            elif action == "d":  # save table region
                cv2.rectangle(img, (x0, y0), (x1, y1), (255, 0, 255), thickness=2)
            elif action == "f":  # save figure region
                cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 255), thickness=2)
            i += 1
    return img


def save_template(raw_img, cells, kvs, actions, keys):
    cells = np.asarray(cells).reshape((-1, 4))
    cell_index = []
    for tx0, ty0, tx1, ty1 in cells:
        index = []
        for i, (x0, y0, x1, y1) in enumerate(kvs):
            if tx0 < (x0 + x1) / 2 < tx1 and ty0 < (y0 + y1) / 2 < ty1:
                index.append(i)
        cell_index.append(index)

    if len(kvs) == 0:
        return None

    template = {}
    template["size"] = raw_img.shape[:2]
    template["kvs"] = kvs
    template["actions"] = actions
    template["cells"] = cells
    template["cell_index"] = cell_index
    if len(keys) > 0:
        template["keys"] = keys

    template_folder = "template"
    num = len(glob.glob(template_folder + "/*.json")) + 1
    with open(f"{template_folder}/{num}.json", 'w') as f:
        json.dump(template, f, ensure_ascii=False, cls=NpEncoder)

    img = draw_actions(raw_img, kvs, actions)
    Image.fromarray(img).save(f"{template_folder}/{num}.png")
    return template


def scale(img):
    img_np = np.asarray(img)
    min, max = np.min(img_np), np.max(img_np)
    img_ = Image.fromarray(np.uint8((img_np - min) / (max - min) * 255))
    return img_


def contrast(img, a):
    enh_con = ImageEnhance.Contrast(img)
    img_ = enh_con.enhance(a)
    return img_


def gaussian_filter(img, radius):
    return img.filter(ImageFilter.GaussianBlur(radius))


def get_perspective(src_corner):
    width = int(
        max(np.linalg.norm(src_corner[0] - src_corner[1]), np.linalg.norm(src_corner[2] - src_corner[3])))
    height = int(
        max(np.linalg.norm(src_corner[0] - src_corner[3]), np.linalg.norm(src_corner[1] - src_corner[2])))
    dst_corner = np.array(((0, 0),
                           (width - 1, 0),
                           (width - 1, height - 1),
                           (0, height - 1)), np.float32)
    M, _ = cv2.findHomography(src_corner, dst_corner, cv2.RANSAC, 10)
    return M, width, height


def remove_overlap(cnts):
    # 去重叠
    cnts = sorted(cnts, key=cv2.contourArea)
    i = 0
    while i < len(cnts) - 1:
        p1 = Polygon(cnts[i].squeeze())
        j = i + 1
        while j < len(cnts):
            p2 = Polygon(cnts[j].squeeze())
            intersection = p1.intersection(p2)
            overlap_ratio = intersection.area / p1.area
            if overlap_ratio > 0.5:
                del cnts[j]
            j += 1
        i += 1
    return cnts


def extract_table(img):
    try:
        h, w = img.size[:2]
        thres = (h + w) // 200
        print(f"size: {(w, h)}, thres: {thres}")
        # col_lines, row_lines, min_rect = get_table_ceilboxes(img, prob=0.5, row=thres, col=thres, alph=thres)
        col_lines, row_lines, min_rect = get_table_ceilboxes(img, alph=thres)

        mask = np.zeros((w, h), dtype='uint8')
        mask = draw_lines(mask, col_lines + row_lines, color=255, lineW=1)
        M, width, height = get_perspective(min_rect)
        if M is None or len(col_lines) < 2 or len(row_lines) < 2:
            return None, None, None
        else:
            warp_img = cv2.warpPerspective(np.asarray(img), M, (width, height))
            warp_mask = cv2.warpPerspective(mask, M, (width, height))
            margin = 1
            warp_mask[:margin, :] = 255
            warp_mask[-margin:, :] = 255
            warp_mask[:, :margin] = 255
            warp_mask[:, -margin:] = 255
            # show_image(warp_mask)

            cnts, _ = cv2.findContours(warp_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[1:]
            cnts = remove_overlap(cnts)

            rects = [cv2.boundingRect(cnt) for cnt in cnts]
            h_thres = int(np.median([h for x, y, w, h in rects]) / 4)
            w_thres = int(np.median([w for x, y, w, h in rects]) / 4)
            cells = [[(x, y), (x + w, y + h)] for x, y, w, h in rects if w > w_thres and h > h_thres]
            return warp_img, warp_mask, cells
    except Exception as e:
        return None, None, None


def extract_table_debug(img):
    try:
        return extract_table(img)
    except Exception as e:
        print(f"Exception: {e}!!!")
        print("no table lines found")
        return None, None, None


def find_closest(query, gallery, k):
    tree = KDTree(gallery)
    return tree.query(query, k)


def find_template(cells, w, h):
    paths = np.asarray(glob.glob("template/*.json"))

    cells = np.asarray(cells).reshape((-1, 4))
    match_template = None
    match_index = None
    match_path = None
    best_score = math.inf
    for path in paths:
        with open(path) as f:
            template = json.load(f)
        template_cells = np.asarray(template["cells"])
        template_kvs = np.asarray(template["kvs"])
        template_h, template_w = template["size"]
        w_ratio = w / template_w
        h_ratio = h / template_h
        if len(template_cells) > 0:
            template_cells[:, [0, 2]] = template_cells[:, [0, 2]] * w_ratio
            template_cells[:, [1, 3]] = template_cells[:, [1, 3]] * h_ratio
            template["cells"] = template_cells
        template_kvs[:, [0, 2]] = template_kvs[:, [0, 2]] * w_ratio
        template_kvs[:, [1, 3]] = template_kvs[:, [1, 3]] * h_ratio
        template["kvs"] = template_kvs

        cost_matrix = np.zeros((len(cells), len(template_cells)))
        for i in range(len(cells)):
            for j in range(len(template_cells)):
                cost = sum(np.abs(cells[i] - template_cells[j]))
                cost_matrix[i, j] = cost
        row_ind, col_ind = linear_sum_assignment(cost_matrix)  # 匈牙利算法求解最优匹配问题
        score = 0
        if len(row_ind) > 0:
            for row, col in zip(row_ind, col_ind):
                score += cost_matrix[row, col]
            score *= (1 + abs((w / h) - (template_w / template_h)))
            print(score, path)
            if score < best_score:
                best_score = score
                match_template = template
                match_path = path
                match_index = col_ind

    thres = w * h / 200
    print(f"threshold: {thres}")
    if best_score > thres:
        match_template = None
        print("no template found")
    else:
        print(f"find template: {match_path}")
        kvs = np.asarray(match_template["kvs"])
        template_cells = np.asarray(match_template["cells"])[match_index]
        cell_index = np.asarray(match_template["cell_index"])[match_index]
        for cell, template_cell, index in zip(cells, template_cells, cell_index):
            if len(index) > 0:
                shift = cell[:2] - template_cell[:2]
                resize = (cell[2:] - cell[:2]) / (template_cell[2:] - template_cell[:2])
                if max(resize) / min(resize) > 2 or min(resize) < 0.5:
                    continue
                align_kvs = kvs[index]
                shift = np.asarray(list(shift) * 2)
                align_kvs = align_kvs + shift
                align_shift = align_kvs[0, :2]
                align_kvs[:, :2] = (align_kvs[:, :2] - align_shift) * resize + align_shift
                align_kvs[:, 2:] = (align_kvs[:, 2:] - align_shift) * resize + align_shift
                kvs[index] = align_kvs
        match_template["kvs"] = kvs

    return match_template


def merge_cells(ori_cells, char_info, font_size):
    def get_region(cells, axis, xmax, thres):
        xs = cells[:, axis]
        xs = xs.reshape(-1, 1)
        cluster = DBSCAN(eps=thres, min_samples=1).fit(xs)
        xlabels = cluster.labels_
        xlabel_set = set(xlabels)
        num_col = len(xlabel_set)
        print(f"num of regions: {num_col}")
        cxs = [np.median(xs[np.where(xlabels == i)]) for i in xlabel_set] + [xmax]
        cxs = np.sort(cxs)
        cxs = (cxs[1:] + cxs[:-1]) / 2
        return num_col, cxs

    cells = np.asarray(ori_cells).reshape(-1, 4)
    xmax, ymax = np.max(cells[:, 2]), np.max(cells[:, 3])
    thres = font_size * 1.5

    num_col, cxs = get_region(cells, 0, xmax, thres)
    num_row, cys = get_region(cells, 1, ymax, thres)

    rowspan_array = np.ones((num_row, num_col), int)
    colspan_array = np.ones((num_row, num_col), int)
    df = pd.DataFrame([[""] * num_col] * num_row)
    for x0, y0, x1, y1 in cells:
        text = match_text(x0, y0, x1, y1, char_info, font_size)
        rowspan_index = np.where((cys > y0) & (cys < y1))[0]
        rowspan = len(rowspan_index)
        colspan_index = np.where((cxs > x0) & (cxs < x1))[0]
        colspan = len(colspan_index)
        if rowspan == 0 or colspan == 0:
            continue
        rid = rowspan_index[0]
        cid = colspan_index[0]
        df.iloc[rid, cid] = text
        if rowspan > 1:
            rowspan_array[rowspan_index[0], cid] = rowspan
            rowspan_array[rowspan_index[1]:rowspan_index[-1] + 1, cid] = 0
        if colspan > 1:
            colspan_array[rid, colspan_index[0]] = colspan
            colspan_array[rid, colspan_index[1]:colspan_index[-1] + 1] = 0
    return df, rowspan_array, colspan_array


def match_text(x0, y0, x1, y1, char_info, font_size):
    same_row = []
    txts = []
    last_y = char_info[0][0][1]
    for i, [[x, y], t] in enumerate(char_info):
        if x0 < x < x1 and y0 < y < y1:
            if abs(y - last_y) < font_size:
                same_row.append(t)
            else:
                last_y = y
                if len(same_row) > 0:
                    txt = "".join(same_row)
                    txts.append(txt)
                same_row = [t]
    txt = "".join(same_row)
    txts.append(txt)
    text = text_postprocess("\n".join(txts))
    return text


def text_postprocess(text):
    return re.sub("(^(/|\||,|，|\\||、|\\\|:|：)*)|((/|\||,|，|\\||、|\\\|:|：)*$)", "", text)


def html_to_list(html):
    df = pd.read_html(html)[0]
    df.columns = df.values[0, :]
    df = df.drop(index=0)
    df = df.drop(index=df[df.isnull().all(axis=1)].index)
    df = df.reset_index(drop=True)
    ret = []
    cols = df.columns.dropna()
    for i in range(len(df)):
        tmp_dict = {}
        for col in cols:
            tmp_dict[col] = df.loc[i, col]
        ret.append(tmp_dict)
    return ret


def df_to_html(df, rowspan_array, colspan_array):
    row_codes = ''
    for rid, r in enumerate(df.values):
        row_code = ''
        for cid, c in enumerate(r):
            rowspan = rowspan_array[rid, cid]
            colspan = colspan_array[rid, cid]
            if rowspan == 1 and colspan == 1:
                row_code += f'<td>{c}</td>'
            elif rowspan > 1 and colspan == 1:
                row_code += f'<td rowspan=\"{rowspan}\">{c}</td>'
            elif rowspan == 1 and colspan > 1:
                row_code += f'<td colspan=\"{colspan}\">{c}</td>'
            elif rowspan > 1 and colspan > 1:
                row_code += f'<td rowspan=\"{rowspan}\" colspan=\"{colspan}\">{c}</td>'
        row_codes += f'<tr>{row_code}</tr>'
    html_code = f'<html>{html_head}<body><table>{row_codes}</table></body></html>'
    # html_code = html_code.replace('\n', '<br/>')
    return html_code


def display_result(source_img, vis_img, save_path):
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.imshow(source_img)
    plt.title("source")
    plt.xticks([])
    plt.yticks([])

    plt.subplot(2, 1, 2)
    plt.imshow(vis_img)
    plt.title("result")
    plt.tight_layout()
    plt.xticks([])
    plt.yticks([])
    plt.savefig(save_path, dpi=300, bbox_inches='tight')


def detect_all():
    table_ocr = TableOCR(use_pp=False)
    save_folder = "/home/igor/zjlab/result/tablebank_line2/"
    if os.path.exists(save_folder):
        shutil.rmtree(save_folder)
    os.makedirs(save_folder)

    paths = glob.glob('/media/igor/8b22d829-1858-4156-81b5-877c76c233491/dataset/TableBank/Recognition/images/*/*')
    df = pd.read_csv("/home/igor/zjlab/result/tablebank_line.csv")
    for i in range(len(df)):
        df.iloc[i, 0] = df.iloc[i, 0].replace("_line.png", ".png")
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
        try:
            table_ocr(img, save_path)
        except Exception as e:
            print(f"Exception: {e}!!!")
            table_ocr.save_ret(save_path + "_fail", "", {}, img)
    total_time = time.time() - start
    avg_time = total_time / num_file
    print(f"all time: {total_time}")
    print(f"average time: {total_time}/{num_file}={avg_time}")
    with open("log.txt", "w") as f:
        f.write(str(avg_time))


def decode(actions):
    dict_str = ""
    i = 0
    for k, action in enumerate(actions):
        if action == 'a':
            dict_str += f"'{i}':"
            i += 1
        elif action == 's':
            dict_str += f"'{i}',"
            i += 1
        elif action == 'd':
            if k == 0 or actions[k - 1] != 'a':
                dict_str += "'table':"
            dict_str += f"'{i}',"
            i += 1
        elif action == 'f':
            if k == 0 or actions[k - 1] != 'a':
                dict_str += "'image':"
            dict_str += f"'{i}',"
            i += 1
        elif action == 'q':
            dict_str += "{"
        elif action == 'w':
            dict_str += "},"
        elif action == 'e':
            dict_str += "["
        elif action == 'r':
            dict_str += "],"
    # return eval("{" + dict_str + "}")
    return dict_str


def process_pdf(basename, img_path):
    pdf2png(img_path, basename)
    imgs = []
    paths = glob.glob(f"{basename}/*.png")
    paths.sort()
    for path in paths:
        img = Image.open(path).convert("RGB")
        img = preprocess_image(img)
        imgs.append(img)
    img = np.vstack(imgs)
    return img


def detect():
    table_ocr = TableOCR(use_pp=False, kie=False, lang="ch")
    img_path = f"data/chouyang.png"
    basename, ext = osp.splitext(img_path)
    if ext == '.pdf':
        img = process_pdf(osp.splitext(img_path)[0], img_path)
        full_img = True
    else:
        img = Image.open(img_path).convert("RGB")
        full_img = False
    table_ocr(img, f"/tmp/algo/{osp.splitext(osp.split(img_path)[1])[0]}", full_img=full_img)


def split_rows_by_enter(path, save_path):
    df = pd.read_excel(path)
    columns = df.columns
    data = df.values
    ret = [columns]
    for row in data:
        cols = []
        count = []
        for d in row:
            ss = str(d).split('\n')
            count.append(len(ss))
            cols.append(ss)
        num_row = max(count)
        cols = [ss + [''] * (num_row - len(ss)) for ss in cols]
        rows = np.array(cols).T.tolist()
        ret += rows

    ret = np.array(ret)
    result = None
    for i in range(len(columns)):
        rows = []
        count = []
        for d in ret[:,i]:
            ss = str(d).replace('  ', ' ').split(' ')
            count.append(len(ss))
            rows.append(ss)
        num_col = max(count)
        rows = [ss + [''] * (num_col - len(ss)) for ss in rows]
        cols = np.array(rows)
        if result is None:
            result = cols
        else:
            result = np.hstack([result, cols])
    new_df = pd.DataFrame(result, columns=None)
    new_df.to_excel(save_path, index=None)


if __name__ == '__main__':
    # detect()

    # path = 'data/19.xlsx'
    # split_rows_by_enter(path, path.replace('.xlsx', '_split.xlsx'))

    table_ocr = TableOCR(use_pp=False, kie=False, lang="ch")
    for img_path in glob.glob('data/*.png'):
        img = Image.open(img_path).convert("RGB")
        w, h = img.size
        img = img.resize((w//4,h//4))
        filename = osp.splitext(osp.split(img_path)[1])[0]
        save_folder = f"data/{filename}"
        table_ocr(img, save_folder, full_img=False)
        split_rows_by_enter(save_folder+'/result_line.xlsx', f'data/{filename}_split.xlsx')
