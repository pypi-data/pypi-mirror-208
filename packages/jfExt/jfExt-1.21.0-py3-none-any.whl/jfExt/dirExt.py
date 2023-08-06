# -*- coding: utf-8 -*-
"""
jfExt.dirExt.py
~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""

import os


def dir_tar_current_path():
    """
    >>> 当前目录下所有子文件夹打包成tar
    """
    paths = os.listdir('./')
    for path in paths:
        if os.path.isdir(path) and (len(path) > 0 and path[0] != '.'):
            cmd = 'tar cvf "{}.tar" "{}"'.format(path, path)
            print(os.system(cmd))


if __name__ == '__main__':
    dir_tar_current_path()
