# -*- coding:utf-8 -*-
# Created at 2015/5/4
# Original Code Created at 2015/4/27
# Modified at 2015/5/4
"""
    Function:
        找到重复次数超过50的package。只找代表元素。
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

    """
    Connect to the Database and get input and output collection.
    """
    conn = pymongo.MongoClient(get_config('database', 'db_host'), int(get_config('database', 'db_port')))
    db = conn[get_config('database', 'db_name')]
    dep_packages = db[get_config('database', 'db_dep_pack')]
    gt_x_list = open(get_config('packages_list', 'gt_50'), 'w')
    for package in dep_packages.find({'status': 1, 'total_num': {'$gt': 20}}):
        if package['path'] == package['dep_parent']:
            gt_x_list.write(package['path']+'\t'+str(package['api_dict'])+'\n')
    gt_x_list.close()


if __name__ == '__main__':
    time_recorder = TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()
