# -*- coding:utf-8 -*-
# Created at 2015-05-15
__author__ = 'Marchon'
import os
import glob
import sys


def main_func():
    """
    对label-all-result.txt 进行分析。
    找到概率高于60%的。
    并且按照cluster大小进行排列。
    :return:
    """

    def get_item(path, p_list):
        for p in p_list:
            if p[0] == path:
                return p

    cluster_info = open("../get_statistics/cluster_size.txt", "r")
    label_source = open("label-all-result.txt", "r")

    # Read label source and put them into a list.
    label_list = []
    for package in label_source:
        items = package.strip('\n').split('\t')
        label_list.append(items)
        # print items
        # exit()

    # Read Cluster Information and output package into a new file.
    label_analysis = open('label_analysis.txt', 'w')
    item_list = []
    for cluster in cluster_info:
        item = get_item(cluster.split('\t')[0], label_list)
        p_type = "Other"
        probability = 0.0
        p_index = -1
        for index in [2, 4, 6, 8, 10, 12]:
            # deal with game, we need a higher threshold
            if index == 8:
                if float(item[index]) > 0.5 and float(item[index]) > probability:
                    p_type = item[index - 1]
                    p_index = index/2
                    probability = item[index]
            else:
                if float(item[index]) > 0.3 and float(item[index]) > probability:
                    p_type = item[index - 1]
                    p_index = index/2
                    probability = item[index]

        new_item = (item[0], p_index, p_type, probability, cluster.split('\t')[1])
        item_list.append(new_item)
        label_analysis.write(item[0]+'\t'+p_type+'\t'+str(probability)+'\t'+cluster.split('\t')[1]+'\n')
    label_analysis.close()
    if len(glob.glob('classification')) >= 1:
        sys.stderr.write('Already have a Directory named "classification"')
        exit()
    os.mkdir('classification')
    for item in item_list:
        file_writer = open('classification\\'+item[2]+'.txt', 'a')
        file_writer.write(item[0]+'\t'+str(item[3])+'\t'+item[4])
        file_writer.close()


if __name__ == '__main__':
    main_func()
