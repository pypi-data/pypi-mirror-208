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
