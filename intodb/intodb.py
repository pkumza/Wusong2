# -*- coding:utf-8 -*-
# Created at 2015/4/27
# Modified at 2015/4/29
# @deprecated at 2015/4/29
"""
    Function:
        search over [smalipath](in intodb.conf) and extract all the features into mongoDB database.
        Target Database and Collection are defined in intodb.conf too.
    功能：
        遍历intodb.conf文件中的smalipath，然后提取所有的内容到mongoDB的数据库中。
        目标数据库和目标数据集在intodb.conf中定义

    Usage:
        Modify intodb.conf, then just run this code or import intodb.py then call function 'main_func()'.
    用法：
        修改intodb.conf的设置，然后运行本代码，或者import intodb.py之后调用main_func()方法即可。

"""
__author__ = 'Marchon'

import ConfigParser
import pymongo
import os
import re
import glob

# 字符串API的匹配
p = re.compile(r'Landroid/.*?;?\-?>*?\(|Ljava/.*?;?\-?>*?\(|Ljavax/.*?;?\-?>*?\(|Lunit/.*?;?\-?>*?\('
               r'|Lorg/apache/commons/logging/.*?;?\-?>*?\(|Lorg/apache/http/.*?;?\-?>*?\(|Lorg/json/.*?;'
               r'?\-?>*?\(|Lorg/w3c/.*?;?\-?>*?\(|Lorg/xml/.*?;?\-?>*?\(|Lorg/xmlpull/.*?;?\-?>*?\(|'
               r'Lcom/android/internal/util.*?;?\-?>*?\(')


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
    db_api_dict = db.cdict
    apidict = {}

    def get_number(string):
        if string not in apidict:
            apidict[string] = len(apidict)
        db_api_dict.insert({"key": string, "value": len(apidict)})
        return str(apidict[string])

    find_file = re.compile(r'.smali$')

    def into_db(apk_path):
        if os.path.exists(apk_path+'/smali'):
            os.chdir(apk_path+'/smali')
            all_over(apk_path, apk_path+'/smali')
            os.chdir(apk_path)

    def all_over(apk_path, path):
        all_thing = glob.glob('*')
        this_call_num = 0
        this_dict = {}
        for thing in all_thing:
            if os.path.isdir(thing):
                os.chdir(path+'\\'+thing)
                # 合并字典
                child = all_over(apk_path, path+'\\'+thing)
                if child is not None:
                    this_dict.update(child)
                os.chdir(path)
            else:
                try:
                    if not find_file.search(thing):
                        continue
                    f = open(thing, 'r')
                    for u in f:
                        match = p.findall(u)
                        for syscall in match:
                            this_call_num += 1
                            call_num = get_number(syscall)
                            if call_num in this_dict:
                                this_dict[call_num] += 1
                            else:
                                this_dict[call_num] = 1
                    f.close()
                except Exception as ex:
                    print('Can not Open ' + thing + ' Wrong with:' + str(ex))
        logs = ['Landroid/util/Log;->v(', 'Landroid/util/Log;->e(', 'Landroid/util/Log;->w(',
                'Landroid/util/Log;->i(', 'Landroid/util/Log;->d(']
        for log in logs:
            if get_number(log) in this_dict:
                del this_dict[get_number(log)]
        if len(this_dict) == 0:
            return
        package = {'apk': apk_path, 'path': path, 'total_num': len(this_dict),
                   'total_call': this_call_num, 'api_dict': this_dict}
        packages.insert(package)
        return this_dict

    dirs = glob.glob(get_config('smalipath', 'smali_path')+'\\*')
    apk_count = 0
    for apk in dirs:
        print apk_count
        apk_count += 1
        print 'APK: ' + apk
        try:
            into_db(apk)
        except Exception as e:
            print 'Wrong Here' + str(e)


if __name__ == '__main__':
    main_func()