#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      models
   Description:
   Author:          dingyong.cui
   date：           2023/5/11
-------------------------------------------------
   Change Activity:
                    2023/5/11
-------------------------------------------------
"""
from pydantic import BaseModel
from typing import Text, Union


class Mask(BaseModel):
    type: Text
    page: Union[int, Text]
    x: int
    y: int
    width: int
    height: int
