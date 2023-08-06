# copyright (c) 2020 PaddlePaddle Authors. All Rights Reserve.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import os

from PIL import Image, ImageDraw
import numpy as np
from pptools.infer.utility import draw_ocr_box_txt, str2bool, init_args as infer_args
import cv2
import imgkit


def init_args():
    parser = infer_args()

    # params for output
    parser.add_argument("--output", type=str, default='./output')
    # params for table structure
    parser.add_argument("--table_max_len", type=int, default=488)
    parser.add_argument("--table_algorithm", type=str, default='TableAttn')
    parser.add_argument("--table_model_dir", type=str)
    parser.add_argument(
        "--merge_no_span_structure", type=str2bool, default=True)
    parser.add_argument(
        "--table_char_dict_path",
        type=str,
        default="../ppocr/utils/dict/table_structure_dict.txt")
    # params for layout
    parser.add_argument("--layout_model_dir", type=str)
    parser.add_argument(
        "--layout_dict_path",
        type=str,
        default="../ppocr/utils/dict/layout_dict/layout_publaynet_dict.txt")
    parser.add_argument(
        "--layout_score_threshold",
        type=float,
        default=0.5,
        help="Threshold of score.")
    parser.add_argument(
        "--layout_nms_threshold",
        type=float,
        default=0.5,
        help="Threshold of nms.")
    # params for kie
    parser.add_argument("--kie_algorithm", type=str, default='LayoutXLM')
    parser.add_argument("--ser_model_dir", type=str)
    parser.add_argument(
        "--ser_dict_path",
        type=str,
        default="../train_data/XFUND/class_list_xfun.txt")
    # need to be None or tb-yx
    parser.add_argument("--ocr_order_method", type=str, default=None)
    # params for inference
    parser.add_argument(
        "--mode",
        type=str,
        default='structure',
        help='structure and kie is supported')
    parser.add_argument(
        "--image_orientation",
        type=bool,
        default=False,
        help='Whether to enable image orientation recognition')
    parser.add_argument(
        "--layout",
        type=str2bool,
        default=True,
        help='Whether to enable layout analysis')
    parser.add_argument(
        "--table",
        type=str2bool,
        default=True,
        help='In the forward, whether the table area uses table recognition')
    parser.add_argument(
        "--ocr",
        type=str2bool,
        default=True,
        help='In the forward, whether the non-table area is recognition by ocr')
    # param for recovery
    parser.add_argument(
        "--recovery",
        type=str2bool,
        default=False,
        help='Whether to enable layout of recovery')
    parser.add_argument(
        "--save_pdf",
        type=str2bool,
        default=False,
        help='Whether to save pdf file')
    parser.add_argument(
        "--gpu_id",
        type=int,
        default=0,
        help='gpu id')

    return parser


def parse_args():
    parser = init_args()
    return parser.parse_args()


def draw_structure_result(image, result, font_path):
    html_head = '<head>' \
                '<meta charset="UTF-8">' \
                '<style>table {border-collapse: collapse;}</style>' \
                '<style>table, th, td {border: 1px solid black;}</style>' \
                '</head>'
    img_left, img_right = draw_ocr_box_txt(
        Image.fromarray(image), result, font_path=font_path, drop_score=0)

    for region in result:
        if region['type'] == 'table':
            x0, y0, x1, y1 = region['bbox']
            w0, h0 = x1 - x0, y1 - y0
            html = region['res']['html'].replace("<html>", f"<html>{html_head}")
            tmp_path = 'tmp.jpg'
            imgkit.from_string(html, tmp_path)
            table_img = Image.open(tmp_path)
            os.remove(tmp_path)
            bw = table_img.convert('L')
            bw = 255 - np.array(bw)
            cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            x, y, w, h = cv2.boundingRect(cnts[-1])
            table_img = np.array(table_img)[y:y + h, x:x + w]
            if w / h < w0 / h0:
                w1, h1 = int(w * h0 / h), h0
            else:
                w1, h1 = w0, int(h * w0 / w)
            table_img = cv2.resize(table_img, (w1, h1))
            img_right[y0:y0 + h1, x0:x0 + w1] = table_img
        elif region['type'] in ['figure', 'equation']:
            x0, y0, x1, y1 = region['bbox']
            img_right[y0:y1, x0:x1] = image[y0:y1, x0:x1]
    h, w = image.shape[:2]
    img_show = Image.new('RGB', (w * 2, h), (255, 255, 255))
    img_show.paste(Image.fromarray(img_left), (0, 0, w, h))
    img_show.paste(Image.fromarray(img_right), (w, 0, w * 2, h))

    return img_show
