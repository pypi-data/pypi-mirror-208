# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import subprocess

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'
import cv2
import json
import re
import numpy as np
import time
import logging
from ppocr.utils.utility import get_image_file_list, check_and_read
from ppocr.utils.logging import get_logger
from pptools.infer.predict_system import TextSystem
from ppstructure.layout.predict_layout import LayoutPredictor
from ppstructure.table.predict_table import TableSystem, to_excel
from ppstructure.utility import parse_args, draw_structure_result
from ppstructure.table.matcher import TableMatch

logger = get_logger()


class NpEncoder(json.JSONEncoder):
    """Convert numpy classes to JSON serializable objects."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


class StructureSystem(object):
    def __init__(self, args):
        self.mode = args.mode
        self.recovery = args.recovery
        self.matcher = TableMatch(filter_ocr_result=True)
        self.image_orientation_predictor = None
        if args.image_orientation:
            import paddleclas
            self.image_orientation_predictor = paddleclas.PaddleClas(
                model_name="text_image_orientation")

        if self.mode == 'structure':
            if not args.show_log:
                logger.setLevel(logging.INFO)
            if args.layout == False and args.ocr == True:
                args.ocr = False
                logger.warning(
                    "When args.layout is false, args.ocr is automatically set to false"
                )
            args.drop_score = 0
            # init model
            self.layout_predictor = None
            self.text_system = None
            self.table_system = None
            if args.layout:
                self.layout_predictor = LayoutPredictor(args)
                if args.ocr:
                    self.text_system = TextSystem(args)
            if args.table:
                if self.text_system is not None:
                    self.table_system = TableSystem(
                        args, self.text_system.text_detector,
                        self.text_system.text_recognizer)
                else:
                    self.table_system = TableSystem(args)

        elif self.mode == 'kie':
            raise NotImplementedError

    def __call__(self, img, return_ocr_result_in_table=False, img_idx=0):
        time_dict = {
            'image_orientation': 0,
            'layout': 0,
            'table': 0,
            'table_match': 0,
            'det': 0,
            'rec': 0,
            'kie': 0,
            'all': 0
        }
        start = time.time()
        if self.image_orientation_predictor is not None:
            tic = time.time()
            cls_result = self.image_orientation_predictor.predict(
                input_data=img)
            cls_res = next(cls_result)
            angle = cls_res[0]['label_names'][0]
            cv_rotate_code = {
                '90': cv2.ROTATE_90_COUNTERCLOCKWISE,
                '180': cv2.ROTATE_180,
                '270': cv2.ROTATE_90_CLOCKWISE
            }
            if angle != '0':
                img = cv2.rotate(img, cv_rotate_code[angle])
            toc = time.time()
            time_dict['image_orientation'] = toc - tic
        if self.mode == 'structure':
            ori_im = img.copy()
            if self.layout_predictor is not None:
                layout_res, elapse = self.layout_predictor(img)
                time_dict['layout'] += elapse
            else:
                h, w = ori_im.shape[:2]
                layout_res = [dict(bbox=None, label='table')]

            res_list = []
            ocr_img = img.copy()
            layout_bbox = []
            for region in layout_res:
                if region['bbox'] is not None:
                    x1, y1, x2, y2 = region['bbox']
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                else:
                    x1, y1, x2, y2 = 0, 0, w, h
                layout_bbox.append([x1, y1, x2, y2])
            layout_bbox = np.array(layout_bbox)

            outliers = []
            for i, region in enumerate(layout_res):
                x1, y1, x2, y2 = layout_bbox[i]
                if i < len(layout_res) - 1:
                    match_index = self.matcher.match_result(layout_bbox[i + 1:], [layout_bbox[i]])
                    if len(match_index) > 0:
                        for match in match_index[0]:
                            j = i + match + 1
                            x3, y3, x4, y4 = layout_bbox[j]
                            if (x1 - x2) * (y1 - y2) > (x3 - x4) * (y3 - y4):
                                outliers.append(j)
                            else:
                                outliers.append(i)
                if region['label'].lower() in ['figure', 'table', 'equation']:
                    ocr_img[y1:y2, x1:x2] = (255, 255, 255)

            inliers = [i for i in range(len(layout_res)) if i not in outliers]
            layout_bbox = layout_bbox[inliers]
            layout_res = np.array(layout_res)[inliers]

            ocr_res = []
            ocr_bbox = []
            if self.text_system is not None:
                filter_boxes, filter_rec_res, ocr_time_dict = self.text_system(ocr_img)
                time_dict['det'] += ocr_time_dict['det']
                time_dict['rec'] += ocr_time_dict['rec']

                # remove style char,
                # when using the recognition model trained on the PubTabNet dataset,
                # it will recognize the text format in the table, such as <b>
                style_token = [
                    '<strike>', '<strike>', '<sup>', '</sub>', '<b>',
                    '</b>', '<sub>', '</sup>', '<overline>',
                    '</overline>', '<underline>', '</underline>', '<i>',
                    '</i>'
                ]
                for box, rec_res in zip(filter_boxes, filter_rec_res):
                    rec_str, rec_conf = rec_res[:2]
                    for token in style_token:
                        if token in rec_str:
                            rec_str = rec_str.replace(token, '')
                    ocr_res.append({
                        'text': rec_str,
                        'confidence': float(rec_conf),
                        'text_region': box.tolist()
                    })
                    ocr_bbox.append([box[0][0], box[0][1], box[2][0], box[2][1]])

            ocr_res = np.array(ocr_res)
            match_index = self.matcher.match_result(ocr_bbox, layout_bbox)
            for i, region in enumerate(layout_res):
                x1, y1, x2, y2 = layout_bbox[i]
                roi_img = ori_im[y1:y2, x1:x2, :]
                label = region['label'].lower()
                res = {}
                if label in ['header', 'footer']:
                    continue
                elif label in ['reference']:
                    label = 'text'
                elif label == 'table':
                    if self.table_system is not None:
                        res, table_time_dict = self.table_system(
                            roi_img, return_ocr_result_in_table)
                        time_dict['table'] += table_time_dict['table']
                        time_dict['table_match'] += table_time_dict['match']
                        time_dict['det'] += table_time_dict['det']
                        time_dict['rec'] += table_time_dict['rec']
                elif i in match_index.keys():
                    res = ocr_res[match_index[i]]
                if len(res) > 0:
                    if label == 'table_caption':
                        if not res[0]['text'].startswith('表'):
                            label = 'text'
                    elif label == 'figure_caption':
                        if not res[0]['text'].startswith('图'):
                            label = 'text'
                res_list.append({
                    'type': label,
                    'bbox': [x1, y1, x2, y2],
                    'img': roi_img,
                    'res': res,
                    'img_idx': img_idx
                })
            end = time.time()
            time_dict['all'] = end - start
            return res_list, time_dict
        elif self.mode == 'kie':
            raise NotImplementedError
        return None, None


def save_structure_res(res, save_folder, img_name, img_idx=0):
    def module(region, xml_txt):
        for text_result in region['res']:
            label = text_result['label']
            box = text_result['text_region']
            xml_txt += f'<{label} coords="{int(box[0][0])},{int(box[0][1])},{int(box[2][0])},{int(box[2][1])}">{text_result["text"]}</{label}>\n'
        return xml_txt

    save_folder = os.path.join(save_folder, img_name)
    os.makedirs(save_folder, exist_ok=True)
    res = sorted(res, key=lambda x: (x['bbox'][1], x['bbox'][0]))
    xml_txt = ''
    for region in res:
        type = region['type']
        x1, y1, x2, y2 = region['bbox']
        if type == 'table_caption':
            xml_txt += f'<table>\n'
            xml_txt = module(region, xml_txt)
        elif type == 'table' and len(region['res']) > 0 and 'html' in region['res']:
            excel_path = os.path.join(
                save_folder,
                '{}_{}.xlsx'.format(region['bbox'], img_idx))
            html_str = region['res']['html']
            to_excel(html_str, excel_path)
            html_xml = re.findall(r"<table>(.+?)</table>", html_str)[0]
            xml_txt += f'<tbody coords="{x1},{y1},{x2},{y2}">{html_xml}</tbody>\n</table>\n'
        elif type == 'figure':
            img_path = os.path.join(
                save_folder,
                '{}_{}.jpg'.format(region['bbox'], img_idx))
            cv2.imwrite(img_path, region['img'])
            xml_txt += f'<figure>\n<fbody coords="{x1},{y1},{x2},{y2}">{img_path}</fbody>\n'
        elif type == 'figure_caption':
            xml_txt = module(region, xml_txt)
            xml_txt += f'</figure>\n'
        elif type == 'equation':
            img_path = os.path.join(
                save_folder,
                '{}_{}.jpg'.format(region['bbox'], img_idx))
            cv2.imwrite(img_path, region['img'])
            xml_txt += f'<equation coords="{x1},{y1},{x2},{y2}">{img_path}</equation>\n'
        else:
            xml_txt = module(region, xml_txt)
    # xml_txt = '<?xml version="1.0"?>\n<body>\n'+xml_txt+'</body>\n'
    with open(os.path.join(save_folder, 'result.xml'), 'w', encoding='utf8') as f:
        f.write(xml_txt)


def main(args):
    image_file_list = get_image_file_list(args.image_dir)
    image_file_list = image_file_list
    image_file_list = image_file_list[args.process_id::args.total_process_num]

    structure_sys = StructureSystem(args)
    img_num = len(image_file_list)
    save_folder = os.path.join(args.output, structure_sys.mode)
    os.makedirs(save_folder, exist_ok=True)

    for i, image_file in enumerate(image_file_list):
        logger.info("[{}/{}] {}".format(i, img_num, image_file))
        img, flag_gif, flag_pdf = check_and_read(image_file)
        img_name = os.path.basename(image_file).split('.')[0]

        if not flag_gif and not flag_pdf:
            img = cv2.imread(image_file)

        if not flag_pdf:
            if img is None:
                logger.error("error in loading image:{}".format(image_file))
                continue
            imgs = [img]
        else:
            imgs = img

        all_res = []
        for index, img in enumerate(imgs):
            res, time_dict = structure_sys(img, img_idx=index)
            if structure_sys.mode == 'structure' and res != []:
                save_structure_res(res, save_folder, img_name, index)
                draw_img = draw_structure_result(img, res, args.vis_font_path)
                img_save_path = os.path.join(save_folder, img_name,
                                             'show_{}.jpg'.format(index))
            elif structure_sys.mode == 'kie':
                raise NotImplementedError
                # draw_img = draw_ser_results(img, res, args.vis_font_path)
                # img_save_path = os.path.join(save_folder, img_name + '.jpg')
            if res != []:
                cv2.imwrite(img_save_path, draw_img)
                logger.info('result save to {}'.format(img_save_path))
            if args.recovery and res != []:
                from ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
                h, w, _ = img.shape
                res = sorted_layout_boxes(res, w)
                all_res += res

        if args.recovery and all_res != []:
            try:
                convert_info_docx(img, all_res, save_folder, img_name,
                                  args.save_pdf)
            except Exception as ex:
                logger.error("error in layout recovery image:{}, err msg: {}".
                             format(image_file, ex))
                continue
        logger.info("Predict time : {:.3f}s".format(time_dict['all']))


if __name__ == "__main__":
    args = parse_args()
    if args.use_mp:
        p_list = []
        total_process_num = args.total_process_num
        for process_id in range(total_process_num):
            cmd = [sys.executable, "-u"] + sys.argv + [
                "--process_id={}".format(process_id),
                "--use_mp={}".format(False)
            ]
            p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stdout)
            p_list.append(p)
        for p in p_list:
            p.wait()
    else:
        main(args)
