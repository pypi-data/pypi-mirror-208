#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：      downloader
   Description:
   Author:          dingyong.cui
   date：           2023/5/6
-------------------------------------------------
   Change Activity:
                    2023/5/6
-------------------------------------------------
"""
import os
import tempfile
import uuid
from urllib import request


def download_file_from_url(url: str, directory=None, filename=None):
    """
    Download the file from the url and save it in the provided directory.
    If directory is None, save it in a temp directory.
    Save the file with the provided filename.
    If the filename is None, try to check if the URL contains a valid filename.
    If the URL contains a valid filename, use that as a filename.
    if the URL does not contain a filename save it as a temporary filename by creating a uuid
    """
    if directory is None:
        directory = tempfile.gettempdir()
    if filename is None:
        filename = str(uuid.uuid4()) + '.' + url.split('.')[-1]
    file_path = os.path.join(directory, filename)
    request.urlretrieve(url, file_path)
    return file_path


def get_filename_from_url(url):
    """
    Check if the URL contains a valid filename.
    If the URL contains a valid filename, return the filename.
    if the URL does not contain a filename return None
    """
    filename = None
    if url is not None:
        filename = url.split('/')[-1]
        if '.' not in filename:
            filename = None
    return filename
