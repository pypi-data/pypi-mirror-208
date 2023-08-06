#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_ocr
   Description:
   Author:          dingyong.cui
   date：           2023/5/12
-------------------------------------------------
   Change Activity:
                    2023/5/12
-------------------------------------------------
"""
import cv2
from pytesseract import pytesseract

from visual_compare.doc.image.compare_image import CompareImage


class TestOcr:

    def setup(self):
        # from visual_compare.doc.visual_test import VisualTest
        # self.cls = VisualTest
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_xxx(self):
        img = self.get_path('1.jpg')
        # ci = cv2.imread(img)
        # gray_image = cv2.cvtColor(ci, cv2.COLOR_BGR2GRAY)
        # threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        #
        ocr_config = '--psm 11' + f' -l eng+jpn'
        # pytesseract.get_languages()
        d = pytesseract.image_to_data(CompareImage(img).opencv_images[0], output_type='dict', config=ocr_config)
        n_boxes = len(d['text'])
        text_list = []
        left_list = []
        top_list = []
        width_list = []
        height_list = []
        conf_list = []
        text_content = []
        # For each detected part
        for j in range(n_boxes):

            # If the prediction accuracy greater than %50
            if int(float(d['conf'][j])) > 20:
                text_list.append(d['text'][j])
                left_list.append(d['left'][j])
                top_list.append(d['top'][j])
                width_list.append(d['width'][j])
                height_list.append(d['height'][j])
                conf_list.append(d['conf'][j])
        text_content.append(
            {'text': text_list, 'left': left_list, 'top': top_list, 'width': width_list, 'height': height_list,
             'conf': conf_list})
        print(text_content)

    def test_torch(self):
        import torch
        pth_file = r'C:\Users\dingyong.cui\.EasyOCR\model\japanese_g2.pth'
        net = torch.load(pth_file, map_location=torch.device('cpu'))
        print(net['model'])
        for k, v in dict(net).items():
            print(k)
            print(v)

    def test_x(self):
        import easyocr
        img1 = self.get_path('1.jpg')
        img_np = cv2.imread(img1)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        # 阈值二进制 - > 127 设置为255(白)，否则0(黑) -> 淡白得更白,淡黑更黑
        _, img_thresh = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)
        # 图像 OCR 识别
        reader = easyocr.Reader(['ja', 'en'], detector=True, recognizer=True)
        text = reader.readtext(img_thresh, detail=0, batch_size=1, paragraph=True)
        print(text)
