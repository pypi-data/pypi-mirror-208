import cv2
import numpy as np


def show_image(src, window_name="img"):
    cv2.namedWindow(window_name, 0)
    cv2.resizeWindow(window_name, 1600, 900)
    cv2.imshow(window_name, src)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def draw_lines(im, bboxes, color=(0, 0, 0), lineW=3):
    """
        boxes: bounding boxes
    """
    tmp = np.copy(im)
    c = color
    h, w = im.shape[:2]
    i = 0
    for box in bboxes:
        if len(box) == 2:
            (x1, y1), (x2, y2) = box
        else:
            x1, y1, x2, y2 = box
        cv2.line(tmp, (int(x1), int(y1)), (int(x2), int(y2)), c, lineW, lineType=cv2.LINE_AA)
        i += 1
    return tmp


def get_line_para(line):
    '''简化交点计算公式'''
    a = line[1] - line[3]
    b = line[2] - line[0]
    c = line[0] * line[3] - line[2] * line[1]
    return a, b, c


def get_cross_point(line1, line2):
    '''计算交点坐标，此函数求的是line1中被line2所切割而得到的点，不含端点'''
    a1, b1, c1 = get_line_para(line1)
    a2, b2, c2 = get_line_para(line2)
    d = a1 * b2 - a2 * b1
    p = [0, 0]
    if d == 0:  # d为0即line1和line2平行
        return ()
    else:
        p[0] = round((b1 * c2 - b2 * c1) * 1.0 / d, 2)  # 工作中需要处理有效位数，实际可以去掉round()
        p[1] = round((c1 * a2 - c2 * a1) * 1.0 / d, 2)
    p = tuple(p)
    return p


def point2point_dist(pt1, pt2):
    return np.linalg.norm(np.asarray(pt1) - np.asarray(pt2))


def point2line_dist(point, line):
    """
    Args:
        point: [x0, y0]
        line: [x1, y1, x2, y2]
    """
    point = np.asarray(point)
    line = np.asarray(line)
    line_point1, line_point2 = line[0:2], line[2:]
    vec1 = line_point1 - point
    vec2 = line_point2 - point
    distance = np.abs(np.cross(vec1, vec2)) / np.linalg.norm(line_point1 - line_point2)
    return distance


def fit_line(p1, p2):
    """A = Y2 - Y1
       B = X1 - X2
       C = X2*Y1 - X1*Y2
       AX+BY+C=0
    直线一般方程
    """
    x1, y1 = p1
    x2, y2 = p2
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2
    return A, B, C


def sqrt(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def point_line_cor(p, A, B, C):
    ##判断点与之间的位置关系
    # 一般式直线方程(Ax+By+c)=0
    x, y = p
    r = A * x + B * y + C
    return r


def line_to_line(points1, points2, alpha=10):
    """
    线段之间的距离
    """
    x1, y1, x2, y2 = points1
    ox1, oy1, ox2, oy2 = points2
    A1, B1, C1 = fit_line((x1, y1), (x2, y2))
    A2, B2, C2 = fit_line((ox1, oy1), (ox2, oy2))
    flag1 = point_line_cor([x1, y1], A2, B2, C2)
    flag2 = point_line_cor([x2, y2], A2, B2, C2)

    if ((flag1 > 0 and flag2 > 0) or (flag1 < 0 and flag2 < 0)) and (A1 * B2 - A2 * B1 != 0):
        x = (B1 * C2 - B2 * C1) / (A1 * B2 - A2 * B1)
        y = (A2 * C1 - A1 * C2) / (A1 * B2 - A2 * B1)
        p = (x, y)
        r0 = sqrt(p, (x1, y1))
        r1 = sqrt(p, (x2, y2))

        if min(r0, r1) < alpha:

            if r0 < r1:
                points1 = [p[0], p[1], x2, y2]
            else:
                points1 = [x1, y1, p[0], p[1]]

    return points1


def detect_lines(image, minLineLength, maxLineGap, scale=30):
    """
    :param scale: kernel size = line image h or w / scale
    :return: rois: [table_i:[array of region of interest in the source image, [top-left_x,top-left_y, width, height]
    horizontal: horizontal lines image: thresh mode
    vertical: vertical lines image: thresh mode
    """
    kernel = 3
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -10)
    horizontal = thresh
    vertical = thresh

    horizontalsize = int(horizontal.shape[0] / scale)
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure, (-1, -1), iterations=3)
    horizontal = cv2.dilate(horizontal, horizontalStructure, (-1, -1), iterations=3)
    horizontal = cv2.blur(horizontal, (kernel, kernel))

    verticalsize = int(vertical.shape[1] / scale)
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    vertical = cv2.erode(vertical, verticalStructure, (-1, -1))
    vertical = cv2.dilate(vertical, verticalStructure, (-1, -1))
    vertical = cv2.blur(vertical, (kernel, kernel))

    # show_image(horizontal)
    # show_image(vertical)
    horizontal = cv2.HoughLinesP(horizontal, 2, np.pi / 180, 150, minLineLength=minLineLength, maxLineGap=maxLineGap)
    vertical = cv2.HoughLinesP(vertical, 2, np.pi / 180, 150, minLineLength=minLineLength, maxLineGap=maxLineGap)
    horizontal = np.squeeze(horizontal).tolist()
    vertical = np.squeeze(vertical).tolist()
    return horizontal, vertical


def adjust_lines(row_lines, col_lines, alph=50):
    ##调整line

    nrow = len(row_lines)
    ncol = len(col_lines)
    new_row_lines = []
    new_col_lines = []
    for i in range(nrow):

        x1, y1, x2, y2 = row_lines[i]
        cx1, cy1 = (x1 + x2) / 2, (y1 + y2) / 2
        for j in range(nrow):
            if i != j:
                x3, y3, x4, y4 = row_lines[j]
                cx2, cy2 = (x3 + x4) / 2, (y3 + y4) / 2
                if (x3 < cx1 < x4 or y3 < cy1 < y4) or (x1 < cx2 < x2 or y1 < cy2 < y2):
                    continue
                else:
                    r = sqrt((x1, y1), (x3, y3))
                    if r < alph:
                        new_row_lines.append([x1, y1, x3, y3])
                    r = sqrt((x1, y1), (x4, y4))
                    if r < alph:
                        new_row_lines.append([x1, y1, x4, y4])

                    r = sqrt((x2, y2), (x3, y3))
                    if r < alph:
                        new_row_lines.append([x2, y2, x3, y3])
                    r = sqrt((x2, y2), (x4, y4))
                    if r < alph:
                        new_row_lines.append([x2, y2, x4, y4])

    for i in range(ncol):
        x1, y1, x2, y2 = col_lines[i]
        cx1, cy1 = (x1 + x2) / 2, (y1 + y2) / 2
        for j in range(ncol):
            if i != j:
                x3, y3, x4, y4 = col_lines[j]
                cx2, cy2 = (x3 + x4) / 2, (y3 + y4) / 2
                if (x3 < cx1 < x4 or y3 < cy1 < y4) or (x1 < cx2 < x2 or y1 < cy2 < y2):
                    continue
                else:
                    r = sqrt((x1, y1), (x3, y3))
                    if r < alph:
                        new_col_lines.append([x1, y1, x3, y3])
                    r = sqrt((x1, y1), (x4, y4))
                    if r < alph:
                        new_col_lines.append([x1, y1, x4, y4])

                    r = sqrt((x2, y2), (x3, y3))
                    if r < alph:
                        new_col_lines.append([x2, y2, x3, y3])
                    r = sqrt((x2, y2), (x4, y4))
                    if r < alph:
                        new_col_lines.append([x2, y2, x4, y4])

    return new_row_lines, new_col_lines


def get_table_ceilboxes(img, alph):
    """
    获取单元格
    """
    ori_row_lines, ori_col_lines = detect_lines(np.array(img), alph, alph/2)

    # new_row_lines, new_col_lines = adjust_lines(row_lines, col_lines, alph=alph)
    # row_lines = new_row_lines + row_lines
    # col_lines = col_lines + new_col_lines

    # h, w = img.size
    # mask = np.zeros((w, h), dtype='uint8')
    # mask = draw_lines(mask, row_lines + col_lines, color=255, lineW=3)
    # show_image(mask)

    row_lines = sorted(ori_row_lines, key=lambda x: x[1] + x[3])
    col_lines = sorted(ori_col_lines, key=lambda x: x[0] + x[2])

    left_col, right_col, top_row, bottom_row = col_lines[0], col_lines[-1], row_lines[0], row_lines[-1]

    col_weight = np.median(
        [point2line_dist(col1[:2], col2) for col1, col2 in zip(col_lines[:-1], col_lines[1:])])
    print(f"col weight: {col_weight}")

    # 填补左边缺失的线
    sorted_row_lines = sorted(row_lines, key=lambda x: x[0])
    anchor = sorted_row_lines[0]
    a, b = [point2line_dist(row_line[:2], left_col) for row_line in sorted_row_lines[:2]]
    if a > col_weight / 2 and abs(a - b) < col_weight / 10:
        left_col = [anchor[0], left_col[1], left_col[2] - left_col[0] + anchor[0],
                    left_col[3]]
        col_lines.append(left_col)

    # 填补右边缺失的线
    sorted_row_lines = sorted(row_lines, key=lambda x: -x[2])
    anchor = sorted_row_lines[0]
    a, b = [point2line_dist(row_line[2:], right_col) for row_line in sorted_row_lines[:2]]
    if a > col_weight / 2 and abs(a - b) < col_weight / 10:
        right_col = [anchor[2], right_col[1], right_col[2] - right_col[0] + anchor[2],
                     right_col[3]]
        col_lines.append(right_col)

    nrow = len(row_lines)
    ncol = len(col_lines)
    for i in range(nrow):
        for j in range(ncol):
            row_lines[i] = line_to_line(row_lines[i], col_lines[j], alph)
            col_lines[j] = line_to_line(col_lines[j], row_lines[i], alph)

    # h, w = img.size
    # mask = np.zeros((w, h), dtype='uint8')
    # mask = draw_lines(mask, col_lines + row_lines, color=255, lineW=3)
    # show_image(mask)

    top_left = get_cross_point(left_col, top_row)
    top_right = get_cross_point(right_col, top_row)
    bottom_right = get_cross_point(right_col, bottom_row)
    bottom_left = get_cross_point(left_col, bottom_row)
    min_rect = np.array((top_left,
                         top_right,
                         bottom_right,
                         bottom_left), np.float32)
    return col_lines, row_lines, min_rect
