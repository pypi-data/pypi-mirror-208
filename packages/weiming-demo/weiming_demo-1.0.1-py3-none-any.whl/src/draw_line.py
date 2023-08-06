import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

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
        if abs(x - point1[0]) > abs(y - point1[1]):
            cv2.line(img2, point1, (x, point1[1]), (255, 0, 0), thickness=2)
        else:
            cv2.line(img2, point1, (point1[0], y), (255, 0, 0), thickness=2)
        cv2.imshow(name, img2)

    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放，显示
        if abs(x - point1[0]) > abs(y - point1[1]):
            point2 = (x, point1[1])
        else:
            point2 = (point1[0], y)
        if point1 != point2:
            g_rect = [point1, point2]


def manual_draw_line(raw_img):
    '''
    获得用户ROI区域的rect=[x,y,w,h]
    :param raw_img:
    :return:
    '''
    global img, name, g_rects, cells
    img = cv2.cvtColor(raw_img, cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]
    comment_h = w // 10
    fontsize = comment_h // 5
    comment_img = np.zeros((comment_h, w, 3), np.uint8)
    comment = "Drag the left mouse button to draw the lines\n" \
              "Press \"s\" to save the line\n" \
              "Press \"z\" to withdraw\n" \
              "Press \"Enter\" to save all results and exit"
    comment_img = Image.fromarray(comment_img)
    draw = ImageDraw.Draw(comment_img)
    fontStyle = ImageFont.truetype("/etc/fonts/simsun.ttc", fontsize, encoding="utf-8")
    draw.text((0, 0), comment, (0, 0, 255), font=fontStyle)
    comment_img = np.asarray(comment_img)
    img = np.vstack((img, comment_img))

    name = "Draw line"
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, 1600, 900)
    margin = (h + w) // 100
    print(f"margin: {margin}")
    while True:
        cv2.setMouseCallback(name, on_mouse)
        # cv2.startWindowThread() # 加在这个位置
        cv2.imshow(name, img)
        key = cv2.waitKey(0)
        if key == 13:  # 按回车键退出
            break
        if key == ord("s"):  # 按s保存
            cv2.rectangle(img, g_rect[0], g_rect[1], (255, 255, 0), thickness=2)
            print("save line")
            (x0, y0), (x1, y1) = g_rect
            if x0 < margin:
                x0 = 0
            if y0 < margin:
                y0 = 0
            if x1 > w - margin:
                x1 = w
            if y1 > h - margin:
                y1 = h
            g_rects.append([(x0, y0), (x1, y1)])
        if key == ord("z"):
            if len(g_rects) > 0:
                cv2.rectangle(img, g_rects[-1][0], g_rects[-1][1], (0, 0, 0), thickness=2)
                del g_rects[-1]
                print("withdraw")
    cv2.destroyWindow(name)
    return g_rects


if __name__ == '__main__':
    img_path = f"../data/test/1.jpg"
    img = np.asarray(Image.open(img_path).convert("RGB"))
    mask = manual_draw_line(img)
    mask = manual_draw_line(img)
