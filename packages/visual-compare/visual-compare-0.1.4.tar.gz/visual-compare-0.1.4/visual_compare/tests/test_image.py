#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_image
   Description:
   Author:          dingyong.cui
   date：           2023/5/11
-------------------------------------------------
   Change Activity:
                    2023/5/11
-------------------------------------------------
"""


class TestImage:

    def setup(self):
        from visual_compare.doc.image.image import MatchImg
        self.cls = MatchImg
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_parse_mask(self):
        img1 = self.get_path('123.png')
        img11 = self.get_path('000.png')
        img2 = self.get_path('124.png')
        res = self.cls().parse_mask(img1, img11)
        print(res)

    def test_parse_mask(self):
        img1 = self.get_path('123.png')
        img11 = self.get_path('000.png')
        img2 = self.get_path('124.png')
        res = self.cls().parse_mask(img1, img11)
        print(res)
