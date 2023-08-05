#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_downloader
   Description:
   Author:          dingyong.cui
   date：           2023/5/11
-------------------------------------------------
   Change Activity:
                    2023/5/11
-------------------------------------------------
"""
import pytest
from visual_compare.utils import downloader


@pytest.mark.parametrize('url,per_res', [
    ('https://www.baidu.com', True),
])
def test_is_url(url, per_res):
    res = downloader.is_url(url)
    assert res == per_res


def test_download_file_from_url():
    downloader.download_file_from_url('asdas')
