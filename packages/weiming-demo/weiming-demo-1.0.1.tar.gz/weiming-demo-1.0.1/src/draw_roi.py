import cv2
import numpy as np
from PIL import Image
import os.path as osp

global img
global point1, point2
global g_rect, g_rects
g_rects = []


def on_mouse(event, x, y, flags, param):
    global img, name, point1, point2, g_rect
    img2 = img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击,则在原图打点
        point1 = (x, y)
        cv2.circle(img2, point1, 10, (255, 0, 0), 5)
        cv2.imshow(name, img2)

    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳，画框
        cv2.rectangle(img2, point1, (x, y), (255, 0, 0), thickness=3)
        cv2.imshow(name, img2)

    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放，显示
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, (255, 0, 0), thickness=3)
        cv2.imshow(name, img2)
        if point1 != point2:
            g_rect = [point1, point2]


def draw_roi(raw_img):
    '''
    获得用户ROI区域的rect=[x,y,w,h]
    :param raw_img:
    :return:
    '''
    global img, name, g_rects, cells
    img = cv2.cvtColor(raw_img, cv2.COLOR_RGB2BGR)

    name = "Draw line"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, 1600, 900)
    while True:
        cv2.setMouseCallback(name, on_mouse)
        cv2.imshow(name, img)
        key = cv2.waitKey(0)
        if key == 13:  # 按回车键退出
            (x1, y1), (x2, y2) = g_rect[0], g_rect[1]
            roi = img[y1:y2, x1:x2]
            break
    cv2.destroyWindow(name)
    return roi


if __name__ == '__main__':
    img_path = f"../data/test/4.jpg"
    img = np.asarray(Image.open(img_path).convert("RGB"))
    roi = draw_roi(img)
    cv2.imwrite(osp.splitext(img_path)[0]+'_roi.png', roi)
