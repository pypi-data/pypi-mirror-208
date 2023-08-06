#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      pdf
   Description:
   Author:          dingyong.cui
   date：           2023/5/15
-------------------------------------------------
   Change Activity:
                    2023/5/15
-------------------------------------------------
"""
import os.path
import uuid
from os.path import split
from typing import List

import cv2

from visual_compare.doc.image.compare_image import CompareImage
from visual_compare.utils.common import check_file_exist


class PDF:
    DPI_DEFAULT = 200
    IMAGE_FORMAT_DEFAULT = 'png'

    def __init__(self, dpi: int = DPI_DEFAULT, image_format: str = None):
        self.dpi = int(dpi)
        if image_format is None:
            self.image_format = self.IMAGE_FORMAT_DEFAULT
        else:
            self.image_format = image_format

    def pdf2image(self, pdf: str, save_to: str = None, get_pdf_content: bool = False, dpi: int = None) -> List[str]:
        image_names = []
        check_file_exist(pdf)
        if dpi is None:
            dpi = self.dpi
        else:
            dpi = int(dpi)
        pdf_compare_img = CompareImage(pdf, get_pdf_content=get_pdf_content, DPI=dpi)
        pdf_ois = pdf_compare_img.opencv_images

        path, filename = split(pdf)
        if save_to is None:
            save_to = os.path.join(os.path.dirname(path), 'pdf_images')
        for i, pi in enumerate(pdf_ois):
            image_name = self.save_image(pi, save_to, str(i + 1))
            image_names.append(image_name)

        return image_names

    def save_image(self, image, filepath: str, suffix: str) -> str:
        image_name = str(str(uuid.uuid1()) + suffix + '.{}'.format(self.image_format))
        image_filepath = os.path.join(filepath, image_name)
        os.makedirs(os.path.dirname(image_filepath), exist_ok=True)
        if self.image_format == 'jpg':
            cv2.imwrite(image_filepath, image, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        else:
            cv2.imwrite(image_filepath, image)

        return image_name
