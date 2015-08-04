# -*- coding:utf-8 -*-
# Created at 2015-05-14
__author__ = 'Marchon'
from helper.config import *
import helper.timer
import pymongo


def compare_package(a, b):
    return a['dep_num'] - b['dep_num']


def main_func():
    """
    Main Function.
    get largest cluster
    找到聚类内容最多的cluster，然后找到代表元素。
    这就是我们找到的用的次数最多的库。
    :return: None
    """
    conn = pymongo.MongoClient(get_config('gs.conf', 'database', 'db_host'),
                               int(get_config('gs.conf', 'database', 'db_port')))
    db = conn[get_config('gs.conf', 'database', 'db_name')]
    dep_packages = db[get_config('gs.conf', 'database', 'db_dep_pack')]
    package_list = []
    """
    for package in dep_packages.find({'status': 1, 'total_num': {'$gt': 20}}, {'path': 1, 'dep_num': 1, 'dep_parent': 1}):
        if package['path'] == package['dep_parent']:
            package_list.append(package)
    """
    feature1_file = open('../intodb/feature1.txt', 'r')
    for index, line in enumerate(feature1_file):
        print index
        path = line.split('\t')[0]
        cur_p = dep_packages.find_one({'path': path}, {'dep_num': 1, 'path': 1, 'path_parts': 1})
        package_list.append(cur_p)
    feature1_file.close()
    package_list.sort(compare_package)
    package_list.reverse()
    cluster_size_list = open(get_config('gs.conf', 'statistics', 'cluster_size'), 'w')
    for p in package_list:
        cluster_size_list.write(p['path']+'\t'+str(p['dep_num'])+'\n')
    cluster_size_list.close()

    #Edition
    edition_dict = {}
    add_times = {}
    for p in package_list:
        if '/'.join(p['path_parts']) in edition_dict:
            edition_dict['/'.join(p['path_parts'])] += p['dep_num']
            add_times['/'.join(p['path_parts'])] += 1
        else:
            edition_dict['/'.join(p['path_parts'])] = p['dep_num']
            add_times['/'.join(p['path_parts'])] = 1
    result = sorted(edition_dict.items(), key=lambda d: d[1])
    cluster_size_list_with_edition = open(get_config('gs.conf', 'statistics', 'cluster_size_edition'), 'w')
    result.reverse()
    for r in result:
        cluster_size_list_with_edition.write(r[0]+'\t'+str(r[1])+'\t'+str(add_times[r[0]])+'\n')
    cluster_size_list_with_edition.close()


if __name__ == '__main__':
    time_recorder = helper.timer.TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()