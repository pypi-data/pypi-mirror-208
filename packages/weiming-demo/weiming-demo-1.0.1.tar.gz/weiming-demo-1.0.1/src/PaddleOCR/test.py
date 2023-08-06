import os
import cv2
import sys
sys.path.append(".")
from paddleocr import PPStructure, draw_structure_result, save_structure_res
# from ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx

table_engine = PPStructure(recovery=True, lang="ch")

save_folder = './output'
# img_path = "/home/igor/zjlab/ocr/data/test/template_1.png"
img_path = 'ppstructure/docs/table/table.jpg'
img = cv2.imread(img_path)
result = table_engine(img)
save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

for line in result:
    line.pop('img')
    print(line)

# from PIL import Image
#
# font_path = 'doc/fonts/simfang.ttf'  # PaddleOCR下提供字体包
# image = Image.open(img_path).convert('RGB')
# im_show = draw_structure_result(image, result, font_path=font_path)
# im_show = Image.fromarray(im_show)
# im_show.save('result.jpg')

# h, w, _ = img.shape
# res = sorted_layout_boxes(result, w)
# convert_info_docx(img, res, save_folder, os.path.basename(img_path).split('.')[0])
