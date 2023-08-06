import glob

import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from table_ocr import decode, extract_table, save_template, preprocess_image, process_pdf
import json
import os.path as osp

global img
global point1, point2
global g_rect, g_rects, all_rects
g_rects, all_rects = [], []


def on_mouse(event, x, y, flags, param):
    global img, name, point1, point2, g_rect
    img2 = img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击,则在原图打点
        point1 = (x, y)
        cv2.circle(img2, point1, 10, (0, 0, 0), 5)
        cv2.imshow(name, img2)

    elif event == cv2.EVENT_MBUTTONDOWN:  # 滚轮点击,则选择当前区域
        point1 = (x, y)
        flag = True
        for (x0, y0), (x1, y1) in cells:
            if x0 < x < x1 and y0 < y < y1:
                flag = False
                cv2.rectangle(img2, (x0, y0), (x1, y1), (0, 255, 0), thickness=2)
                g_rect = [(x0, y0), (x1, y1)]
                break
        if flag:
            cv2.circle(img2, point1, 10, (0, 255, 0), 5)
        cv2.imshow(name, img2)

    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳，画框
        cv2.rectangle(img2, point1, (x, y), (0, 0, 0), thickness=2)
        cv2.imshow(name, img2)

    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放，显示
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, (0, 0, 0), thickness=2)
        cv2.imshow(name, img2)
        if point1 != point2:
            g_rect = [point1, point2]


def draw_template_kv(raw_img, rois):
    '''
    获得用户ROI区域的rect=[x,y,w,h]
    :param raw_img:
    :return:
    '''
    global img, name, g_rects, cells
    img = cv2.cvtColor(raw_img, cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    for roi in rois:
        img = cv2.rectangle(img, roi[0], roi[1], (255, 0, 255), 1)
    cells = rois
    comment_h = w // 10
    fontsize = comment_h // 5
    comment_img = np.zeros((comment_h, w, 3), np.uint8)
    comment = "Click the mouse wheel on a highlighted region or drag the left mouse button to draw the region\n" \
              "Press \"a\" to save the key region\n" \
              "Press \"s\" to save the value region\n" \
              "Press \"d\" to save table region\n" \
              "Press \"f\" to save figure region\n" \
              "Press \"q\" to start dict\n" \
              "Press \"w\" to end dict\n"\
              "Press \"e\" to start list\n" \
              "Press \"r\" to end list\n" \
              "Press \"z\" to withdraw\n" \
              "Press \"Enter\" to save all results and exit"
    comment_img = Image.fromarray(comment_img)
    draw = ImageDraw.Draw(comment_img)
    fontStyle = ImageFont.truetype("/etc/fonts/simsun.ttc", fontsize, encoding="utf-8")
    draw.text((0, 0), comment, (0, 0, 255), font=fontStyle)
    comment_img = np.asarray(comment_img)
    img = np.vstack((img, comment_img))

    name = "Draw kv region"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, 1600, 900)

    actions = []
    keys = []
    while True:
        cv2.setMouseCallback(name, on_mouse)
        cv2.imshow(name, img)
        key = cv2.waitKey(0)
        if key == 13:  # enter to return
            break
        action = chr(key)
        if action == "z":  # withdraw
            if len(g_rects) > 0:
                cv2.rectangle(img, g_rects[-1][0], g_rects[-1][1], (0, 0, 0), thickness=2)
                if actions[-1] == 'k':
                    del keys[-1]
                del actions[-1]
                del g_rects[-1]
                print(decode(actions))
        else:
            if action == "a":  # save key region
                g_rects.append(g_rect)
                actions.append(action)
                cv2.rectangle(img, g_rect[0], g_rect[1], (255, 0, 0), thickness=2)
            elif action == "s":  # save value region
                g_rects.append(g_rect)
                actions.append(action)
                cv2.rectangle(img, g_rect[0], g_rect[1], (0, 0, 255), thickness=2)
            elif action == "d":  # save table region
                g_rects.append(g_rect)
                actions.append(action)
                cv2.rectangle(img, g_rect[0], g_rect[1], (255, 0, 255), thickness=2)
            elif action == "f":  # save figure region
                g_rects.append(g_rect)
                actions.append(action)
                cv2.rectangle(img, g_rect[0], g_rect[1], (0, 255, 255), thickness=2)
            elif action == "k":  # key
                key_txt = ''
                while True:
                    key = cv2.waitKey(0)
                    if key == 13:  # enter to return
                        break
                    char = chr(key)
                    key_txt += char
                print(key_txt)
                actions.append(action)
                keys.append(key_txt)
            elif action == "q":  # {
                actions.append(action)
            elif action == "w":  # }
                actions.append(action)
            elif action == "e":  # [
                actions.append(action)
            elif action == "r":  # ]
                actions.append(action)
            print(decode(actions)[-100:])
    cv2.destroyWindow(name)

    kvs = np.asarray(g_rects).reshape((-1, 4))
    actions = "".join(actions)
    return kvs, actions, keys


if __name__ == '__main__':
    img_path = f"/home/igor/zjlab/TBT/data/EU882.pdf"
    basename, ext = osp.splitext(img_path)
    if ext == '.pdf':
        warp_img = process_pdf(basename, img_path)
        cells = []
    else:
        img = Image.open(img_path).convert("RGB")
        img = preprocess_image(img)
        warp_img, warp_mask, cells = extract_table(img)
    # kvs, actions, keys = draw_template_kv(warp_img, cells)
    # template = save_template(warp_img, cells, kvs, actions, keys)

    with open("template/7.json") as f:
        template = json.load(f)
    template = save_template(warp_img, cells, template["kvs"], template["actions"], template["keys"])


