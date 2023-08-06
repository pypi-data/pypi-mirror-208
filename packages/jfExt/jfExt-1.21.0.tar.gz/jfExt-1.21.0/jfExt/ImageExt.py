# -*- coding: utf-8 -*-
"""
jfExt.ImageExt.py
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import tempfile
from fake_useragent import UserAgent
# from PIL import Image
# from PIL import ImageChops
import requests
from jfExt.fileExt import *
from jfExt.BasicType.StringExt import string_random
from jfExt.ValidExt import *


# pragma mark - define
# --------------------------------------------------------------------------------
r = requests.session()
ua = UserAgent()
headers = {
    'user-agent': ua.chrome
}


def image_to_square(in_file, out_file, size=1024, background_color=(255, 255, 255)):
    """
    >>> 图片转换成正方形
    :param {String} in_file: 图片读取地址
    :param {String} out_file: 图片输出地址
    :param {Int} size: 图片长度/宽度
    :param {(Int, Int, Int)} background_color: 背景颜色
    """
    from PIL import Image
    image = Image.open(in_file)
    image = image.convert('RGB')
    w, h = image.size
    # 创建背景图，颜色值为127
    background = Image.new('RGB', size=(max(w, h), max(w, h)), color=(255, 255, 255))
    # 一侧需要填充的长度
    length = int(abs(w - h) // 2)
    # 粘贴的位置
    box = (length, 0) if w < h else (0, length)
    background.paste(image, box)
    # 缩放
    image_data = background.resize((1024, 1024))
    # background.show()
    image_data.save(out_file)


def image_diff(image_a_url, image_b_url):
    """
    >>> 网络图片比较是否相同
    :param {String} image_a_url: 图片A url
    :param {String} image_b_url: 图片B url
    :return {Boolean}: 图片是否相同
    """
    image_a_md5 = string_random(32)
    image_b_md5 = string_random(32)
    # 读取image_a
    with tempfile.NamedTemporaryFile() as fp:
        try:
            if valid_url(image_a_url):
                res = r.get(image_a_url, timeout=2, headers=headers)
                if res.status_code == 200:
                    fp.write(res.content)
                image_a_md5 = file_get_file_md5(fp.name)
        except:
            import traceback
            traceback.print_exc()
            pass
    # 读取image_b
    with tempfile.NamedTemporaryFile(suffix=".png") as fp:
        try:
            if valid_url(image_b_url):
                res = r.get(image_b_url, timeout=2, headers=headers)
                if res.status_code == 200:
                    fp.write(res.content)
                image_b_md5 = file_get_file_md5(fp.name)
        except:
            pass
    if image_a_md5 != image_b_md5:
        return True
    return False


def image_md5(image_url):
    """
    >>> 网络图片比较是否相同
    :param {String} image_url: 图片 url
    :return {String}: 图片md5
    """
    image_md5 = string_random(32)
    # 读取image_a
    with tempfile.NamedTemporaryFile() as fp:
        try:
            if valid_url(image_url):
                res = r.get(image_url, timeout=2, headers=headers)
                if res.status_code == 200:
                    fp.write(res.content)
                image_md5 = file_get_file_md5(fp.name)
        except:
            import traceback
            traceback.print_exc()
            pass
    return image_md5



if __name__ == '__main__':
    a = "https://test.megaplus.co.nz/wp-content/uploads/2023/01/placeholder_v1-398.png"
    b = "https://images.megabit.co.nz/images/megaplus/logo/placeholder_v1.png"
    # b = "https://test-api.megaplus.co.nz/static/upload/imgs/6c8e4f6a45a542ba962a48623b6722fc.jpg"
    print(image_diff(a, b))
    print(image_md5((a)))
