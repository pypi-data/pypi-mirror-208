#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      common
   Description:
   Author:          dingyong.cui
   date：           2023/5/11
-------------------------------------------------
   Change Activity:
                    2023/5/11
-------------------------------------------------
"""
import os
from typing import Union
from urllib import parse


def is_url(url: str) -> bool:
    """
    Check if the provided string is a valid URL.
    """
    try:
        result = parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def check_file_exist(file: Union[str, list]):
    if isinstance(file, list):
        for f in file:
            check_file_exist(f)
    if isinstance(file, str):
        if not os.path.isfile(file) and not is_url(file):
            raise AssertionError(
                'The file does not exist: {}'.format(file))
