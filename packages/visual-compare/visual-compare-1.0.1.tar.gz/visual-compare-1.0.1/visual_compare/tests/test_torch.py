#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      test_torch
   Description:
   Author:          dingyong.cui
   date：           2023/5/15
-------------------------------------------------
   Change Activity:
                    2023/5/15
-------------------------------------------------
"""


def test_x():
    from trdg.generators import (
        GeneratorFromDict,
        GeneratorFromRandom,
        GeneratorFromStrings,
        GeneratorFromWikipedia,
    )

    # The generators use the same arguments as the CLI, only as parameters
    generator = GeneratorFromStrings(
        ['Test1', 'Test2', 'Test3'],
        blur=2,
        random_blur=True
    )

    for img, lbl in generator:
        print(img.show(), lbl)
