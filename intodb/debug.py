
# -*- coding:utf-8 -*-
# Created at 2015/4/27
# Modified at 2015/4/29
"""
    Function:
        Compare packages
    作用：
        比较包

    Usage:
        Modify intodb.conf, then just run this code or import intodb.py then call function 'main_func()'.
    用法：
        修改intodb.conf的设置，然后运行本代码，或者import intodb.py之后调用main_func()方法即可。

    Trivial Notes：
        dep_packages 是第一次运行，然后就是比较普通，没有status概念
        dep_packages2 是第二次运行，运行时间为13min45sec 修复了bug，并加入了status1，2，3
        dep_packages3 进一步修改，加入status4，并且对所有的status进行统计，并且把各种status的情况进行记录。
"""
__author__ = 'Marchon'

import ConfigParser
import pymongo
import sys
import time


def get_config(section, key):
    """
    Load the config File : into_database.conf
    载入设置文件 : into_database.conf
    """
    config = ConfigParser.ConfigParser()
    path = 'into_database.conf'
    config.read(path)
    return config.get(section, key)


class TimeRecord:
    """
    Made for Time Recording.
    用来计时。
    """
    def __init__(self):
        self.init_time = time.time()
        self.if_start = False
        self.start_time = 0

    def start(self):
        self.start_time = time.time()
        self.if_start = True
        print('*' * 60)
        print('Task: '+sys.argv[0]+' Starts.')

    def end(self):
        end_time = time.time()
        if self.if_start:
            task_interval = end_time - self.start_time
            print('Task: '+sys.argv[0]+' Ends.')
            m = int(task_interval) / 60
            s = int(task_interval) % 60
            if m <= 1:
                mi = 'minute'
            else:
                mi = 'minutes'
            if s <= 1:
                se = 'second'
            else:
                se = 'seconds'
            print('Consuming '+str(m)+' '+mi+' and '+str(s)+' '+se+'.')
            print('*' * 60)
        self.if_start = False


def main_func():
    """
    Main Function
    主方法
    """
    conn = pymongo.MongoClient(get_config('database', 'db_host'), int(get_config('database', 'db_port')))
    db = conn[get_config('database', 'db_name')]
    packages = db[get_config('database', 'db_pack')].find().sort([
        ("depth", pymongo.ASCENDING), ("total_call", pymongo.ASCENDING), ('total_num', pymongo.ASCENDING)])
    # package = packages.next()
    dep_packages = db[get_config('database', 'db_dep_pack')]
    for pack in packages:
        a = dep_packages.find_one({"path": pack['path']})
        if a == None:
            print pack


if __name__ == '__main__':
    main_func()