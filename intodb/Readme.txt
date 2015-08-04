dep_statistics.txt 代表着 重复次数 出现次数（其中status为3的直接略过不进行计算。）
status_statistics.txt 代表着状态信息。（以重复次数20为阈值）

    # Status 0 means have not scanned yet. '0' is packages' initial status.
    status_1_cnt = 0                # Status 1 means lib_root
    status_2_cnt = 0                # Status 2 means non-lib
    status_3_cnt = 0                # Status 3 means lib_child
    status_4_cnt = 0                # Status 4 means directory_root

当一个package，发现自己的父文件夹已经是1或者3的时候，直接标注为3，略过不进行比较。