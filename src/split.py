import glob
import itertools
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
import os
import queue
import random
import re

from datetime import datetime
from queue import PriorityQueue
from threading import Lock, Thread


def split(lk, trd_cnt, prt):
    sd = 'graph' if os.getenv('MD', 'G') == 'G' else 'sample'
    st_tm = datetime.strptime(os.getenv('ST_TM', ''), '%Y-%m-%d-%H')
    tr_tm = datetime.strptime(os.getenv('TR_TM', ''), '%Y-%m-%d-%H')
    vd_tm = datetime.strptime(os.getenv('VD_TM', ''), '%Y-%m-%d-%H')
    sp_tm = datetime.strptime(os.getenv('SP_TM', ''), '%Y-%m-%d-%H')
    for fn in glob.glob(f'./data/{sd}/*.txt'):
        fn_tm = datetime.strptime(fn, f'./data/{sd}/%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.hour % trd_cnt != prt:
            continue
        if fn_tm < tr_tm:
            dst = './data/split/train.txt'
        elif fn_tm < vd_tm:
            dst = './data/split/valid.txt'
        else:
            dst = './data/split/test.txt'

        with open(fn, 'r') as fr:
            with lk:
                with open(dst, 'a') as fw:
                    pass
                    fw.write(fr.read())


def main():
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    for i in range(0, trd_cnt):
        t = Thread(target=split, args=(lk, trd_cnt, i))
        t.start()
        t.join()


if __name__ == '__main__':
    main()
    exit(0)
