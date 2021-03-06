# -*- coding:utf-8 -*-
# Created at 2015/5/4
# Original Code Created at 2015/4/27
# Modified at 2015/5/4
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
        dep_packages4 was set for 'package_compare2.py', replace packages.next() with for-loop.
            which successfully fixed a BUG.
        dep_packages5 is for test. because we can't find dep_num in 4
        dep_packages6. In this collection , threshold is set as 50

        package_compare2.py 已经是一个相对较好的脚本了
        package_compare3.py 的目的在于，在十万个数据入库的时候，发生了较大的bug，就是myapp54入了两次，有很多重复。
            写这个3会针对myapp54.txt做特殊处理。最终代码成型发布的时候，需要删掉相关处理内容、
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
    Run this function to compare every package.
    Input is get_config('database', 'db_pack')
    Output is get_config('database', 'db_dep_pack')
    """

    """
    Connect to the Database and get input and output collection.
    """
    conn = pymongo.MongoClient(get_config('database', 'db_host'), int(get_config('database', 'db_port')))
    db = conn[get_config('database', 'db_name')]
    packages = db[get_config('database', 'db_pack')].find().sort([
        ("depth", pymongo.ASCENDING), ("total_call", pymongo.ASCENDING), ('total_num', pymongo.ASCENDING)])
    # package = packages.next()
    dep_packages = db[get_config('database', 'db_dep_pack')]

    """
        Search the packages among the database.
        We ignore packages which depth is 0, because that means it's a library contains the whole APP. We believe root
    directory is not a library.
        Firstly, we put the packages with the same total_call and total_num into a list named 'common',when there's no
    more packages having the same total_call and total_num. Secondly, we compare every package in 'common' list so we
    get every package's parent. At last, calculate the Repetitions as 'dep_num' and insert the packages into a new db
    collection.
        在数据库中对包进行寻找。
        在运行的过程中，会忽略那些深度为0的包。因为那意味着，整个应用都是一个库。
        首先，把相同total_call和total_num的包放到一个list（列表）中，这个list的名字叫做common，当再也没有package有同样的
    参数的时候，计算这个common列表。common中的内容要进行两两比较，找到每个包的parent（也有可能是它自己），计算每一个包的
    重复次数。最后，把新得到的信息，包括status、parent、重复次数，插入数据库的新的数据集合里。
    """
    common = []
    total_call_plat = 0
    total_num_plat = 0
    total_dep_num = {}

    # Status 0 means have not scanned yet. '0' is packages' initial status.
    status_1_cnt = 0                # Status 1 means lib_root
    status_2_cnt = 0                # Status 2 means non-lib
    status_3_cnt = 0                # Status 3 means lib_child
    status_4_cnt = 0                # Status 4 means directory_root
    status_5_cnt = 0                # Status 5 形如一个文件夹，com，只有一个子文件夹com/admob
    dir_parent_dict = {}            # scanned packages' statuses.
    myapp54_list = []
    package_count = -1              # count
    packages_num = packages.count()

    for package in packages:
        package_count += 1

        # Things about myapp54.
        if 'myapp54' in package['path']:
            if package['path'] in myapp54_list:
                continue
            else:
                myapp54_list.append(package['path'])

        # We believe root directory is not a library unless the whole App is a library.
        if package['depth'] == 0:
            package['status'] = 4
            # 注释掉这里，因为有可能超内存？
            #dir_parent_dict[package['path']] = 4
            del package['_id']
            dep_packages.insert(package)
            status_4_cnt += 1
            continue

        # If a package has only one directory, and
        if package['direct_dir_num'] == 1 and package['direct_file_num'] == 0:
            package['status'] = 5
            # 注释掉这里，因为有可能超内存？
            #dir_parent_dict[package['path']] = 5
            del package['_id']
            dep_packages.insert(package)
            status_5_cnt += 1
            continue

        # if this package's dir_parent is lib, there's no need to compare this package any more.
        # 1 means lib_root; 3 means lib_child, so I use Modulo operation here.
        dir_split = package['path'].split('\\')
        dir_parent_split = dir_split[:len(dir_split)-1]
        dir_parent = '\\'.join(dir_parent_split)
        if dir_parent in dir_parent_dict and dir_parent_dict[dir_parent] in [1, 3]:
            # Mark this package as lib_child and insert it into a new Database Collection.
            package['status'] = 3
            dir_parent_dict[package['path']] = 3
            status_3_cnt += 1
            del package['_id']
            dep_packages.insert(package)
            continue

        # len(common) == 0 is used just for the first package comes here.
        # the code in the if-statement will only runs once.
        if len(common) == 0:
            total_call_plat = package['total_call']
            total_num_plat = package['total_num']
            common.append({"package": package, "dep_num": 1, "parent": 0})
        else:
            # if this package is the last package in the database,
            # There's no need to append it into a common list.
            if total_call_plat == package['total_call'] and total_num_plat == package['total_num']\
                    and package_count != packages_num:
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
                            if len(i['package']['path']) < len(j['package']['path']):
                                i['package']['path_parts'] = j['package']['path_parts']
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
                    if i['dep_num'] >= 50:
                        package_featured['status'] = 1          # lib_root
                        status_1_cnt += 1
                    else:
                        # 注释掉这里，因为有可能超内存？
                        package_featured['status'] = 2          # is not lib
                        status_2_cnt += 1
                    dir_parent_dict[package_featured['path']] = package_featured['status']
                    package_featured['dep_parent'] = i['parent']
                    package_featured['dep_num'] = i['dep_num']
                    print package_featured
                    dep_packages.insert(package_featured)
                del common[:]
                # Add three statements here. Actually fixed the Bug in package_compare.py
                total_call_plat = package['total_call']
                total_num_plat = package['total_num']
                common.append({"package": package, "dep_num": 1, "parent": 0})
    """
    This is a copy of code. I put the code here to deal with the last package.
    放在这里用来处理最后一个common list，因为上面的for循环的话，最后一个common list就没办法处理了。
    这就是为什么之前的代码，会发现rep-packages4比packages总量上少一个。
    理论上这些代码只运行一次。
    """
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
        if i['dep_num'] >= get_config('threshold', 'dep_threshold'):
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
    """
    At last, output some statistics into txt file.
    dep_statistics represents the repetitions status.
    status_statistics represents every package's status.
    """
    dep_writer = open(get_config('dep_statistics', 'out_file'), 'w')
    for a, b in [(k, total_dep_num[k]) for k in sorted(total_dep_num.keys())]:
        dep_writer.write(str(a)+'\t'+str(b)+'\n')
    dep_writer.close()
    status_writer = open(get_config('dep_statistics', 'status_statistics'), 'w')
    status_writer.write('Status 1 : '+str(status_1_cnt)+'\n')
    status_writer.write('Status 2 : '+str(status_2_cnt)+'\n')
    status_writer.write('Status 3 : '+str(status_3_cnt)+'\n')
    status_writer.write('Status 4 : '+str(status_4_cnt)+'\n')
    status_writer.write('Status 5 : '+str(status_5_cnt)+'\n')
    for a, b in [(k, dir_parent_dict[k]) for k in sorted(dir_parent_dict.keys())]:
        status_writer.write(str(a)+'\t'+str(b)+'\n')
    status_writer.close()
    print 'Status_1 : '+str(status_1_cnt)
    print 'Status_2 : '+str(status_2_cnt)
    print 'Status_3 : '+str(status_3_cnt)
    print 'Status_4 : '+str(status_4_cnt)
    print 'Status_5 : '+str(status_5_cnt)

if __name__ == '__main__':
    time_recorder = TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()
