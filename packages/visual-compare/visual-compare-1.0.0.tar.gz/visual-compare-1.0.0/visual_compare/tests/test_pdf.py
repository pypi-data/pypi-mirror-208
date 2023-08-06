#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_pdf
   Description:
   Author:          dingyong.cui
   date：           2023/5/15
-------------------------------------------------
   Change Activity:
                    2023/5/15
-------------------------------------------------
"""


class TestPDF:

    def setup(self):
        from visual_compare.doc.pdf import PDF
        self.cls = PDF
        self.image_base = '../../files/images/'

    def get_path(self, filename):
        return self.image_base + filename

    def test_pdf2image(self):
        cls = self.cls()
        reference_image = self.get_path('111.pdf')
        res = cls.pdf2image(reference_image)
        print(res)
