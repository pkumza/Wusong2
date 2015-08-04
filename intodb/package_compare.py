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
    package = packages.next()
    dep_packages = db[get_config('database', 'db_dep_pack')]

    common = []
    total_call_plat = 0
    total_num_plat = 0
    total_dep_num = {}
    status_1_cnt = 0
    status_2_cnt = 0
    status_3_cnt = 0
    status_4_cnt = 0
    dir_parent_dict = {}

    while True:
        # We believe root directory is not a library unless the whole App is a library.
        if package['depth'] == 0:
            package['status'] = 4
            dir_parent_dict[package['path']] = 4
            del package['_id']
            dep_packages.insert(package)
            status_4_cnt += 1
            package = packages.next()
            print 'Status_4 : '+str(status_4_cnt)
            continue
        dir_split = package['path'].split('\\')
        dir_parent_split = dir_split[:len(dir_split)-1]
        dir_parent = '\\'.join(dir_parent_split)

        # if this package's dir_parent is lib, there's no need to compare this package any more.
        # 1 means lib_root; 3 means lib_child, so I use Modulo operation here.
        if dir_parent in dir_parent_dict and dir_parent_dict[dir_parent] % 2 == 1:
            # Mark this package as lib_child and insert it into a new Database Collection.
            package['status'] = 3
            dir_parent_dict[package['path']] = 3
            status_3_cnt += 1
            del package['_id']
            dep_packages.insert(package)
            package = packages.next()
            continue

        if len(common) == 0:
            total_call_plat = package['total_call']
            total_num_plat = package['total_num']
            common.append({"package": package, "dep_num": 1, "parent": 0})
        else:
            if total_call_plat == package['total_call'] and total_num_plat == package['total_num']:
                common.append({"package": package, "dep_num": 1, "parent": 0})
            else:
                print 'Common List Size: '+str(len(common))
                for i in common:
                    if i['parent'] != 0:
                        continue
                    for j in common:
                        if j['parent'] != 0:
                            continue
                        if i['package']['api_dict'] == j['package']['api_dict']:
                            i['dep_num'] += 1
                            j['parent'] = i['package']['path']   # set his parent as i
                        i['parent'] = i['package']['path']       # the parent is himself
                for i in common:
                    if i['parent'] == i['package']['path']:
                        if i['dep_num'] in total_dep_num:
                            total_dep_num[i['dep_num']] += 1
                        else:
                            total_dep_num[i['dep_num']] = 1
                        for j in common:
                            if j['parent'] == i['package']['path']:
                                j['dep_num'] = i['dep_num']
                    package_featured = i['package']
                    del package_featured['_id']
                    # Threshold is set here
                    if i['dep_num'] >= 20:
                        package_featured['status'] = 1          # lib_root
                        status_1_cnt += 1
                    else:
                        package_featured['status'] = 2          # is not lib
                        status_2_cnt += 1
                    dir_parent_dict[package_featured['path']] = package_featured['status']
                    package_featured['dep_parent'] = i['parent']
                    package_featured['dep_num'] = i['dep_num']
                    dep_packages.insert(package_featured)
                del common[:]
        try:
            package = packages.next()
        except Exception as e:
            print str(e)
            break
    dep_writer = open(get_config('dep_statistics', 'out_file'), 'w')
    for a, b in [(k, total_dep_num[k]) for k in sorted(total_dep_num.keys())]:
        dep_writer.write(str(a)+'\t'+str(b)+'\n')
    dep_writer.close()
    status_writer = open(get_config('dep_statistics', 'status_statistics'), 'w')
    status_writer.write('Status 1 : '+str(status_1_cnt)+'\n')
    status_writer.write('Status 2 : '+str(status_2_cnt)+'\n')
    status_writer.write('Status 3 : '+str(status_3_cnt)+'\n')
    status_writer.write('Status 4 : '+str(status_4_cnt)+'\n')
    for a, b in [(k, dir_parent_dict[k]) for k in sorted(dir_parent_dict.keys())]:
        status_writer.write(str(a)+'\t'+str(b)+'\n')
    status_writer.close()
    print 'Status_1 : '+str(status_1_cnt)
    print 'Status_2 : '+str(status_2_cnt)
    print 'Status_3 : '+str(status_3_cnt)
    print 'Status_4 : '+str(status_4_cnt)

if __name__ == '__main__':
    time_recorder = TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()
