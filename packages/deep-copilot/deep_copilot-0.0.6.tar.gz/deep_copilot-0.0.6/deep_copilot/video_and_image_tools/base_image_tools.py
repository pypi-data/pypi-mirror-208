#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/19 下午3:22
# @Author : gyw
# @File : content-service
# @ description:

import requests
from PIL import Image
from io import BytesIO
import os
import uuid
from .opencv_tools import phash


def save_pic_from_url(url, dest_path=None):
    """
    从URL存储图片到本地数据，url是可以直接访问的
    Args:
        url: url路径
        dest_path:存储的路径 None的话，存储在{project_dir}/tmp

    Returns:

    """
    if not dest_path:
        dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp", "pic_tmp")
        os.makedirs(dir_path, exist_ok=True)
        dest_path = os.path.join(dir_path, f'{uuid.uuid1().__str__()}.png')
    resp = requests.get(url)
    byte_stream = BytesIO(resp.content)
    im = Image.open(byte_stream)
    if im.mode == "RGBA":
        im.load()  # required for png.split()
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3])
    im.save(dest_path, "png")
    return dest_path


