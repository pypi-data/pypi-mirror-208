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


class MatchImg:

    def __init__(self, source: str, temp: str, threshold=0.95):
        self.source_img = Image(source)
        self.temp_img = Image(temp)
        self.threshold = threshold

    @property
    def mask(self):
        return self.parse_mask()

    def match_temp(self, method=cv2.TM_CCOEFF_NORMED):
        try:
            mt = cv2.matchTemplate(self.source_img.image, self.temp_img.image, method)
            locations = numpy.where(mt >= self.threshold)

            return list(zip(locations[1], locations[0]))
        except cv2.error as e:
            print(e)

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


class MatchPdf:

    def __init__(self, source, temp: str, threshold=0.05):
        if isinstance(source, str):
            self.source_img = Image(source).image
        else:
            # self.source_img = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
            self.source_img = source
        self.temp_img = Image(temp).image
        self.threshold = threshold

    @property
    def mask(self):
        return self.parse_mask()

    def match_temp(self, method=cv2.TM_CCOEFF_NORMED):
        try:
            ccc = cv2.cvtColor(self.source_img, cv2.COLOR_BGR2GRAY)
            cct = cv2.cvtColor(self.temp_img, cv2.COLOR_BGR2GRAY)
            mt = cv2.matchTemplate(ccc, cct, method)
            locations = numpy.where(mt <= self.threshold)

            return list(zip(locations[1], locations[0]))
        except cv2.error as e:
            print(e)

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
