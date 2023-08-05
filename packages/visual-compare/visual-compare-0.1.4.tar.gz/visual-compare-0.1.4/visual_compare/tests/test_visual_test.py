#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_visual_test
   Description:
   Author:          dingyong.cui
   date：           2023/5/11
-------------------------------------------------
   Change Activity:
                    2023/5/11
-------------------------------------------------
"""


class TestVisualTest:

    def setup(self):
        from visual_compare.doc.visual_test import VisualTest
        self.cls = VisualTest
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_compare_images_with_mask(self):
        reference_image = self.get_path('123.png')
        # mask_images = [self.get_path('000.png'), self.get_path('098.png')]
        mask_images = [self.get_path('000.png')]
        test_image = self.get_path('124.png')
        cls = self.cls()
        mask = cls.generate_mask(reference_image, mask_images)
        res = cls.compare_images(reference_image, test_image, mask=mask)
        print(res)
        assert cls.is_different is True

    def test_compare_images_no_mask(self):
        reference_image = self.get_path('123.png')
        # mask_images = [self.get_path('000.png'), self.get_path('098.png')]
        test_image = self.get_path('124.png')
        cls = self.cls()
        # mask = cls.generate_mask(reference_image, mask_images)
        res = cls.compare_images(reference_image, test_image)
        print(res)
        assert cls.is_different is False
