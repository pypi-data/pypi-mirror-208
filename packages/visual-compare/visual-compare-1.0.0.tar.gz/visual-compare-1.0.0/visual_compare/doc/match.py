#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      match
   Description:
   Author:          dingyong.cui
   date：           2023/5/9
-------------------------------------------------
   Change Activity:
                    2023/5/9
-------------------------------------------------
"""
from os.path import splitext, split

import cv2
import numpy

from visual_compare.doc.image.image import Image
from visual_compare.doc.models import Mask


class Match(object):

    def __init__(self, threshold=0.95, match_method=cv2.TM_CCOEFF_NORMED):
        self.threshold = threshold
        self.match_method = match_method

    def match_temp(self, source_image, temp_image, threshold, method=cv2.TM_CCOEFF_NORMED):
        if threshold is None:
            threshold = self.threshold
        try:
            mt = cv2.matchTemplate(source_image, temp_image, method)
            locations = numpy.where(mt >= threshold)

            return list(zip(locations[1], locations[0]))
        except cv2.error as e:
            print(e)

    def parse_mask(self, source: str, temp: str, threshold: float, match_method: int, mask_type: str, page: str):
        pass


class MatchImg(Match):

    def __init__(self, threshold=0.95, match_method=cv2.TM_CCOEFF_NORMED):
        super().__init__(threshold, match_method)

    def parse_mask(self, source: str, temp: str, threshold=None, match_method=cv2.TM_CCOEFF_NORMED,
                   mask_type='coordinates', page='all'):
        source_img = Image(source)
        temp_img = Image(temp)

        mask_list = []
        match_list = self.match_temp(source_img.image, temp_img.image, threshold, match_method)
        for m in match_list:
            mask = Mask(type=mask_type, page=page, x=m[0], y=m[1], width=temp_img.width, height=temp_img.height)
            mask_list.append(mask.dict())

        return mask_list


class MatchPdf(Match):

    def __init__(self, source, temp: str, threshold=0.05, match_method=cv2.TM_CCOEFF_NORMED):
        super().__init__(threshold, match_method)
        if isinstance(source, str):
            self.source_img = Image(source).image
        else:
            # self.source_img = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
            self.source_img = source
        self.temp_img = Image(temp).image
        self.threshold = threshold

    def parse_mask(self, match_method=cv2.TM_CCOEFF_NORMED):
        mask_list = []
        match_list = self.match_temp(method=match_method)
        for m in match_list:
            mj = {
                'type': 'coordinates',
                "page": "all",
                'x': m[0],
                'y': m[1],
                'width': self.temp_img.width,
                'height': self.temp_img.height
            }
            mask_list.append(mj)

        return mask_list
