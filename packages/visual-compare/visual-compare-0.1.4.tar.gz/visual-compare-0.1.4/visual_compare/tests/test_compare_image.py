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
import cv2
import numpy

from visual_compare.doc.image.compare_image import CompareImage


class TestCompareImage:

    def setup(self):
        from visual_compare.doc.visual_test import VisualTest
        self.cls = VisualTest
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_compare_images(self):
        from visual_compare.doc.image.image import MatchImg
        img1 = self.get_path('123.png')
        img11 = self.get_path('000.png')
        img2 = 'https://zati-public-heimdall-prd.s3.cn-northwest-1.amazonaws.com.cn/za-heimdall/JIRALISTENER/SJ/36ef1e5f58cc6fd1b730c2308610fc83/image001.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA4WFLST4CUDJA5C2L%2F20230511%2Fcn-northwest-1%2Fs3%2Faws4_request&X-Amz-Date=20230511T021610Z&X-Amz-Expires=500&X-Amz-SignedHeaders=host&X-Amz-Signature=7893e08c62d3eadf8f33050c91c37e18c9b2d45f5144f73362966c46cee75295'
        mi = MatchImg(img1, img11)
        mask = mi.mask
        self.cls().compare_images(img1, img2, mask=mask)

    def test_compare_images_show_diff(self):
        from visual_compare.doc.image.image import MatchImg
        img1 = self.get_path('123.png')
        img11 = self.get_path('000.png')
        img2 = self.get_path('124.png')
        mi = MatchImg(img1, img11)
        mask = mi.mask
        self.cls(show_diff=True).compare_images(img1, img2, mask=mask)

    def test_compare_images_check_text_content(self):
        img1 = self.get_path('i1.png')
        img2 = self.get_path('i2.png')
        self.cls().compare_images(img1, img2, check_text_content=False)

    def test_compare_pdf(self):
        img1 = self.get_path('111.pdf')
        img2 = self.get_path('222.pdf')
        self.cls().compare_images(img1, img2)

    def test_compare_pdf_watermark(self):
        img1 = self.get_path('sample_1_page.pdf')
        img2 = self.get_path('sample_1_page_with_watermark.pdf')
        self.cls().compare_images(img1, img2)

    # def test_compare_images_error_size(self):
    #     img1 = self.get_path('y1.png')
    #     img2 = self.get_path('y2.png')
    #     self.cls().compare_images(img1, img2, check_text_content=False)

    def test_compare_images_with_screenshot_dir(self):
        img1 = self.get_path('123.png')
        img2 = self.get_path('124.png')
        screenshot_dir = '/screenshots'
        cls = self.cls(screenshot_dir=screenshot_dir)
        cls.compare_images(img1, img2)
        assert cls.is_different is True

    def test_compare_images_placeholders(self):
        # from visual_compare.doc.image.image import MatchImg
        # img1 = self.get_path('123.png')
        # img11 = self.get_path('000.png')
        # img2 = self.get_path('124.png')
        img1 = self.get_path('111.pdf')
        img11 = self.get_path('333.png')
        img2 = self.get_path('222.pdf')
        # mi = MatchImg(img1, img11)
        # mask = mi.mask
        # self.cls().compare_images(img1, img2, placeholder_file=[img11])
        self.cls().compare_images(img1, img2, check_text_content=True)

    def test_compare_images_watermark(self):
        # from visual_compare.doc.image.image import MatchImg
        # img1 = self.get_path('123.png')
        # img11 = self.get_path('000.png')
        # img2 = self.get_path('124.png')
        img1 = self.get_path('111.pdf')
        img11 = self.get_path('555.png')
        img2 = self.get_path('222.pdf')
        # mi = MatchImg(img1, img11)
        # mask = mi.mask
        try:
            watermark = cv2.imread(img11)
            watermark1 = CompareImage(img1).opencv_images[0]
        except:
            print(111)
        watermark_gray = cv2.cvtColor(
            watermark, cv2.COLOR_BGR2GRAY)
        mt = cv2.matchTemplate(watermark_gray, cv2.cvtColor(watermark1, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED)
        # list(zip(mt[1], mt[0]))
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mt)
        # watermark_gray = (watermark_gray * 255).astype("uint8")
        mask = {
                'type': 'coordinates',
                "page": "all",
                'x': maxLoc[0],
                'y': maxLoc[1],
                'width': watermark.shape[1],
                'height': watermark.shape[0]
            }
        cv2.rectangle(watermark1, (maxLoc[0], maxLoc[1]), (maxLoc[0] + watermark.shape[1], maxLoc[1] + watermark.shape[0]), (255, 0, 0), 3)
        self.cls().compare_images(img1, img2, mask=mask)
        cv2.imshow("Output", watermark1)
        cv2.waitKey(0)

    def test_filetype(self):
        img1 = self.get_path('111.pdf')
        watermark1 = CompareImage(img1).opencv_images[0]
        cv2.imwrite('D://Work//PT//compare//visual_compare//tests//screenshots//1.png', watermark1)
        # cv2.imshow("Output", watermark1)
        # cv2.waitKey(0)
