# -*- coding:utf-8 -*-
# Created at 2015/4/27
# Modified at 2015/4/29
# @deprecated at 2015/4/29
"""
    Function:
        label packages' directory depth. Take toot packages as Zero level.
    作用：
        把packages的数据标记层级。直接出现在root下，也就是smali文件夹下的，为0级。

    Usage:
        Modify intodb.conf, then just run this code or import intodb.py then call function 'main_func()'.
    用法：
        修改intodb.conf的设置，然后运行本代码，或者import intodb.py之后调用main_func()方法即可。

"""
__author__ = 'Marchon'

import ConfigParser
import pymongo


def get_config(section, key):
    """载入设置文件"""
    config = ConfigParser.ConfigParser()
    path = 'intodb.conf'
    config.read(path)
    return config.get(section, key)


def main_func():
    """主方法"""
    conn = pymongo.Connection(get_config('database', 'dbhost'), int(get_config('database', 'dbport')))
    db = conn[get_config('database', 'dbname')]
    packages = db.cpackages
    for package in packages.find():
        path = package['path']
        parts = path.split("\\")
        packages.update({'path': path}, {'$set': {'depth': len(parts)-5}})
        print len(parts)

if __name__ == '__main__':
    main_func()