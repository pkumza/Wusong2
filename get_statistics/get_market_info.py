# -*- coding:utf-8 -*-
# Created at 2015-05-14
__author__ = 'Marchon'
from helper.config import *
import helper.timer
import pymongo


def main_func():
    """
    Main Function.
    get market information.about how many apks in each market.
    :return: None
    """
    conn = pymongo.MongoClient(get_config('gs.conf', 'database', 'db_host'),
                               int(get_config('gs.conf', 'database', 'db_port')))
    db = conn[get_config('gs.conf', 'database', 'db_name')]
    packages = db[get_config('gs.conf', 'database', 'db_pack')]

    baidu = 0
    myapp = 0
    anzhi = 0
    eoe = 0
    gfan = 0

    # 找到所有的root（其实和apk一一对应），然后记录市场就可以了。
    packages_find = packages.find({'depth': 0}, {'apk': 1})
    for index, package_root in enumerate(packages_find):
        # 进度追踪
        # See the progress.
        if index % 100 == 0:
            print index
        '''
        There're five markets:
        baidu. myapp, anzhi, eoe, gfan.
        This can be modified if you have different markets.
        '''
        if 'baidu' in package_root['apk']:
            baidu += 1
        elif 'myapp' in package_root['apk']:
            myapp += 1
        elif 'anzhi' in package_root['apk']:
            anzhi += 1
        elif 'eoemarket' in package_root['apk']:
            eoe += 1
        elif 'gf' in package_root['apk']:
            gfan += 1
        else:
            print 'Not in any of these markets:'
            print package_root['apk']
    market_txt = get_config('gs.conf', 'statistics', 'market')
    market_writer = open(market_txt, 'w')
    market_writer.write('baidu:'+str(baidu)+'\n')
    market_writer.write('myapp:'+str(myapp)+'\n')
    market_writer.write('anzhi:'+str(anzhi)+'\n')
    market_writer.write('eoe:'+str(eoe)+'\n')
    market_writer.write('gfan:'+str(gfan)+'\n')
    market_writer.close()


if __name__ == '__main__':
    time_recorder = helper.timer.TimeRecord()
    time_recorder.start()
    main_func()
    time_recorder.end()