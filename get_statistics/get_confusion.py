# -*- coding:utf-8 -*-
# Created at 2015-05-14
__author__ = 'Marchon'
from helper.config import *
import helper.timer
import pymongo


def main_func():
    prefix_len = len('H:\\4conv_smali\\decoded\\myapp54.txt\\0e20ad7268530576854491d712a9d353.apk\\smali\\')
    package_list = []

    conn = pymongo.MongoClient(get_config('gs.conf', 'database', 'db_host'),
                               int(get_config('gs.conf', 'database', 'db_port')))
    db = conn[get_config('gs.conf', 'database', 'db_name')]
    dep_packages = db[get_config('gs.conf', 'database', 'db_dep_pack')]

    feature1_file = open('../intodb/feature1.txt', 'r')
    confusion = open(get_config('gs.conf', 'statistics', 'confusion'), 'w')
    for index, line in enumerate(feature1_file):
        path = line.split('\t')[0]
        cur_p = dep_packages.find_one({'path': path}, {'dep_num': 1, 'apk': 1, 'path': 1, 'path_parts': 1})

        parts = path[len(cur_p['apk'])+7:].split("\\")

        if cur_p['path_parts'] != parts:
            print index
            origin = 'Origin: '+'/'.join(parts)
            longer = 'Longer: '+'/'.join(cur_p['path_parts'])
            confusion.write(str(index)+'\n'+origin+'\n'+longer+'\n'+'\n')
            print origin
            print longer
            print ''
        '''
        a = len('/'.join(cur_p['path_parts']))+prefix_len
        b = len(cur_p['path'])
        if a != b:
            print a
            print b
            print cur_p['path']
            print cur_p['path_parts']
            print ''
        '''
    confusion.close()
    feature1_file.close()
    print package_list


if __name__ == '__main__':
    time_recorder = helper.timer.TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()