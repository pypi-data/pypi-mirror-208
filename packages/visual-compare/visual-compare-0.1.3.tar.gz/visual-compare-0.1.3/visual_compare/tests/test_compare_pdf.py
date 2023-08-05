#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_compare_image
   Description:
   Author:          dingyong.cui
   date：           2023/5/6
-------------------------------------------------
   Change Activity:
                    2023/5/6
-------------------------------------------------
"""
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager

from visual_compare.doc.image.compare_image import CompareImage
from visual_compare.doc.pdf_test import is_masked


class TestComparePDF:

    def setup(self):
        from visual_compare.doc.pdf_test import PdfTest
        self.cls = PdfTest
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_compare_pdf(self):
        from visual_compare.doc.image.image import MatchImg
        img1 = self.get_path('sample_1_page.pdf')
        img11 = self.get_path('000.png')
        img2 = self.get_path('sample_1_page_different_text.pdf')
        mi = MatchImg(img1, img11)
        mask = [".*JobID.*", ".*RTM.*"]
        self.cls().compare_pdf_documents(img1, img2, compare="text")

    def test_compare_pdf_mask(self):
        from visual_compare.doc.image.image import MatchImg
        img1 = self.get_path('sample_1_page.pdf')
        img11 = self.get_path('000.png')
        img2 = self.get_path('sample_1_page_different_text.pdf')
        mi = MatchImg(img1, img11)
        mask = [".*JobID.*", ".*RTM.*"]
        self.cls().compare_pdf_documents(img1, img2, mask=mask, compare="text")

    def test_xxx(self):
        import fitz
        import cv2
        import pytesseract
        import easyocr

        img1 = self.get_path('111.pdf')
        img11 = self.get_path('333.png')
        img2 = self.get_path('222.pdf')
        mask = [".*Certificate Number.*"]

        reader = easyocr.Reader(['en', 'ja'])
        result = reader.readtext(CompareImage(img1).opencv_images[0])
        for r in result:
            print(r)

        # watermark = cv2.imread(img11)
        # watermark1 = CompareImage(img1).opencv_images[0]
        # pytesseract.image_to_string(
        #     watermark, config='--psm 6').replace("\n\n", "\n")
        # pytesseract.image_to_string(
        #     watermark1, config='--psm 6').replace("\n\n", "\n")
        # ref_doc = fitz.open(img1)
        # for i, page in enumerate(ref_doc.pages()):
        #     pls = page.get_text("text").splitlines()
        # #     for p in pls:
        # #         if is_masked(p, mask):
        # #             print(p)
        # self.cls().compare_pdf_documents(img1, img2, mask=mask, compare="text")
