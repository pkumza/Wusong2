# -*- coding:utf-8 -*-
# Created at 2015/4/29
# Based on intodb.py

"""
    重大错误。
    into_database.conf
    [source_path]
    source_path=H:\4conv_smali\decoded\myapp54.txt;
    出现了两次，造成后面的结果出现大规模的错误。
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










    Repairing failed.










    """

    """
    Connect to the Database and get input and output collection.
    """
    conn = pymongo.MongoClient(get_config('database', 'db_host'), int(get_config('database', 'db_port')))
    db = conn[get_config('database', 'db_name')]
    packages = db[get_config('database', 'db_pack')].find()
    # package = packages.next()
    path_list = []
    for cnt, package in enumerate(packages):
        if 'myapp54' in package['path']:
            if package['path'] in path_list:
                pass
        else:
            print package
            break

    for cnt, package in enumerate(packages):
        print package


if __name__ == '__main__':
    time_recorder = TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()
