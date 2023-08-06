#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      _base
   Description:
   Author:          dingyong.cui
   date：           2023/5/6
-------------------------------------------------
   Change Activity:
                    2023/5/6
-------------------------------------------------
"""
from typing import Union

import cv2
import numpy
import os

from visual_compare.doc.models import Mask
from visual_compare.utils.common import is_url
from visual_compare.utils.downloader import download_file_from_url


class Image:

    def __init__(self, image: str):
        if is_url(image):
            self._image = download_file_from_url(image)
        else:
            self._image = str(image)
        if os.path.isfile(image) is False:
            raise AssertionError('The image file does not exist: {}'.format(image))

    @property
    def image(self):
        return cv2.imread(self._image, cv2.IMREAD_UNCHANGED)

    @property
    def width(self):
        return self.image.shape[1]

    @property
    def height(self):
        return self.image.shape[0]


class MatchImg:

    def __init__(self, threshold=0.95, match_method=cv2.TM_CCOEFF_NORMED):
        self.threshold = threshold
        self.match_method = match_method
        self.match = []

    def match_temp(self, source_image, temp_image, threshold, method=cv2.TM_CCOEFF_NORMED):
        if threshold is None:
            threshold = self.threshold
        source_image = self.uniform_channel(source_image)
        temp_image = self.uniform_channel(temp_image)
        try:
            mt = cv2.matchTemplate(source_image, temp_image, method)
            locations = numpy.where(mt >= threshold)

            return list(zip(locations[1], locations[0]))
        except cv2.error as e:
            print(e)

    @staticmethod
    def uniform_channel(img):
        if img.shape[2] == 4:
            img = img[:, :, :3]

        return img

    # def parse_mask(self, source: str, temp: str, threshold=None, match_method=cv2.TM_CCOEFF_NORMED,
    #                mask_type='coordinates', page: Union[str, int] = 'all'):
    #     source_img = Image(source)
    #     temp_img = Image(temp)
    # 
    #     mask_list = []
    #     match_list = self.match_temp(source_img.image, temp_img.image, threshold, match_method)
    #     for m in match_list:
    #         mask = Mask(type=mask_type, page=1, x=m[0], y=m[1], width=temp_img.width, height=temp_img.height)
    #         mask_list.append(mask.dict())
    # 
    #     return mask_list

    def parse_mask(self, source: Union[str, list], temp: Union[str, list], threshold=None,
                   match_method=cv2.TM_CCOEFF_NORMED, mask_type='coordinates'):
        if isinstance(source, str):
            source = [source]
        if isinstance(temp, str):
            temp = [temp]
        for i, s in enumerate(source):
            # sii = Image(s)
            for t in temp:
                ti = Image(t)
                match_list = self.match_temp(s, ti.image, threshold, match_method)
                if match_list:
                    self.collect(match_list, ti.width, ti.height, mask_type, i + 1)

        return self.match

    def collect(self, match_list: list, width: int, height: int, mask_type: str, page: int):
        for mt in match_list:
            m = Mask(type=mask_type, page=page, x=mt[0], y=mt[1], width=width, height=height)
            self.match.append(m.dict())
