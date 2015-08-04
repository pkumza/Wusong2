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
import os
import sys
import time
import glob
import pymongo
import re


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


def get_feature_1():
    """
    Main Function
    主方法
    """

    """
    Connect to the Database and get input and output collection.
    """
    find_file = re.compile(r'.smali$')

    def search(path):
        this_feature_1 = 0
        all_thing = glob.glob(path+'\\*')
        for thing in all_thing:
            # If the thing is a directory.
            if os.path.isdir(thing):
                # Merge Dictionary
                # 合并字典
                child = search(thing)
                if child is not None:
                    this_feature_1 |= child
            # If the thing is a file
            else:
                try:
                    # Is this file a smali file?
                    if not find_file.search(thing):
                        continue
                    smali_file = open(thing, 'r')
                    for l in smali_file:
                        #if '.super Landroid' in l:
                            #print l
                            #continue
                        if '.super Landroid/app/Activity;' in l:
                            this_feature_1 |= 1
                            pass
                        if '.super Landroid/app/Service;' in l or '.super Landroid/app/IntentService;' in l:
                            pass
                            this_feature_1 |= 2
                        if '.super Landroid/content/BroadcastReceiver;' in l:
                            this_feature_1 |= 4
                        if '.super Landroid/content/ContentProvider;' in l:
                            #print l
                            this_feature_1 |= 8

                    smali_file.close()
                except Exception as e:
                    print str(e)
        return this_feature_1

    gt_x_list = open(get_config('packages_list', 'gt_50'), 'r')
    feature_file = open(get_config('packages_list', 'feature1'), 'w')
    for line in gt_x_list:
        package = line.split('\t')[0]
        this_feature = search(package)
        feature_string = "{"
        feature_string += "'activity':1" if this_feature & 1 > 0 else "'activity':0"
        feature_string += ","
        feature_string += "'service':1" if this_feature & 2 > 0 else "'service':0"
        feature_string += ","
        feature_string += "'content_provider':1" if this_feature & 4 > 0 else "'content_provider':0"
        feature_string += ","
        feature_string += "'broadcast':1" if this_feature & 8 > 0 else "'broadcast':0"
        feature_string += "}"
        feature_file.write(package+'\t'+feature_string+'\n')
        #print package
        #print this_feature
    feature_file.close()
    gt_x_list.close()


def get_feature_3():
    """
    Main Function
    主方法
    """

    """
    Connect to the Database and get input and output collection.
    """
    find_file = re.compile(r'.smali$')

    def search(path):
        this_feature_1 = 0
        all_thing = glob.glob(path+'\\*')
        for thing in all_thing:
            # If the thing is a directory.
            if os.path.isdir(thing):
                # Merge Dictionary
                # 合并字典
                child = search(thing)
                if child is not None:
                    this_feature_1 |= child
            # If the thing is a file
            else:
                try:
                    # Is this file a smali file?
                    if not find_file.search(thing):
                        continue
                    smali_file = open(thing, 'r')
                    for l in smali_file:
                        if 'intent'.lower() in l.lower():
                            print l


                    smali_file.close()
                except Exception as e:
                    print str(e)
        return this_feature_1

    gt_x_list = open(get_config('packages_list', 'gt_50'), 'r')
    feature_file = open(get_config('packages_list', 'feature3'), 'w')
    for line in gt_x_list:
        package = line.split('\t')[0]
        this_feature = search(package)
        feature_string = "{"
        feature_string += "'native_code':1" if this_feature & 1 > 0 else "'native_code':0"
        feature_string += ","
        feature_string += "'reflection':1" if this_feature & 2 > 0 else "'reflection':0"
        feature_string += ","
        feature_string += "'dynamic_loading':1" if this_feature & 4 > 0 else "'dynamic_loading':0"
        feature_string += ","
        feature_string += "'check_permission':1" if this_feature & 8 > 0 else "'check_permission':0"
        feature_string += "}"
        feature_file.write(package+'\t'+feature_string+'\n')
        # print package
        # print this_feature
    feature_file.close()
    gt_x_list.close()


def get_feature_5():
    """
    Main Function
    主方法
    """

    """
    Connect to the Database and get input and output collection.
    """
    find_file = re.compile(r'.smali$')

    def search(path):
        this_feature_1 = 0
        all_thing = glob.glob(path+'\\*')
        for thing in all_thing:
            # If the thing is a directory.
            if os.path.isdir(thing):
                # Merge Dictionary
                # 合并字典
                child = search(thing)
                if child is not None:
                    this_feature_1 |= child
            # If the thing is a file
            else:
                try:
                    # Is this file a smali file?
                    if not find_file.search(thing):
                        continue
                    smali_file = open(thing, 'r')
                    for l in smali_file:
                        if 'invoke-static {v0}, Ljava/lang/System;->load'.lower() in l.lower():
                            this_feature_1 |= 1
                            # print l
                        if 'Ljava/lang/Object;->getClass()'.lower() in l.lower():
                            this_feature_1 |= 2
                            #print l
                            pass
                        if 'Ldalvik/system/DexClassLoader;->loadClass'.lower() in l.lower():
                            this_feature_1 |= 4
                            pass
                        if 'checkCallingPermission'.lower() in l.lower()\
                                or 'checkPermission'.lower() in l.lower()\
                                or 'checkCallingOrSelfPermission'.lower() in l.lower():
                            this_feature_1 |= 8
                            #print l
                            pass

                    smali_file.close()
                except Exception as e:
                    print str(e)
        return this_feature_1

    gt_x_list = open(get_config('packages_list', 'gt_50'), 'r')
    feature_file = open(get_config('packages_list', 'feature5'), 'w')
    for line in gt_x_list:
        package = line.split('\t')[0]
        this_feature = search(package)
        feature_string = "{"
        feature_string += "'native_code':1" if this_feature & 1 > 0 else "'native_code':0"
        feature_string += ","
        feature_string += "'reflection':1" if this_feature & 2 > 0 else "'reflection':0"
        feature_string += ","
        feature_string += "'dynamic_loading':1" if this_feature & 4 > 0 else "'dynamic_loading':0"
        feature_string += ","
        feature_string += "'check_permission':1" if this_feature & 8 > 0 else "'check_permission':0"
        feature_string += "}"
        feature_file.write(package+'\t'+feature_string+'\n')
        # print package
        # print this_feature
    feature_file.close()
    gt_x_list.close()



def get_feature_child_dir():
    """
    Main Function
    主方法
    """
    gt_x_list = open(get_config('packages_list', 'gt_50'), 'r')
    feature_file = open(get_config('packages_list', 'gt_50_2'), 'w')

    conn = pymongo.MongoClient(get_config('database', 'db_host'), int(get_config('database', 'db_port')))
    db = conn[get_config('database', 'db_name')]
    packages = db[get_config('database', 'db_pack')].find().sort([
        ("depth", pymongo.ASCENDING), ("total_call", pymongo.ASCENDING), ('total_num', pymongo.ASCENDING)])
    # package = packages.next()
    dep_packages = db[get_config('database', 'db_dep_pack')]



if __name__ == '__main__':
    time_recorder = TimeRecord()
    time_recorder.start()
    get_feature_5()
    time_recorder.end()
