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


def _split(tr, vd, ts, lk, trd_cnt, prt):
    sd = 'graph' if os.getenv('MD', 'G') == 'G' else 'sample'
    st_tm = datetime.strptime(os.getenv('ST_TM', ''), '%Y-%m-%d-%H')
    tr_tm = datetime.strptime(os.getenv('TR_TM', ''), '%Y-%m-%d-%H')
    vd_tm = datetime.strptime(os.getenv('VD_TM', ''), '%Y-%m-%d-%H')
    sp_tm = datetime.strptime(os.getenv('SP_TM', ''), '%Y-%m-%d-%H')
    for fn in glob.glob(f'./data/{sd}/*.txt'):
        fn_tm = datetime.strptime(fn, f'./data/{sd}/%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
        if fn_tm < tr_tm:
            dst = './data/split/train_d.txt'
        elif fn_tm < vd_tm:
            dst = './data/split/valid_d.txt'
        else:
            dst = './data/split/test_d.txt'

        with open(fn, 'r') as fr:
            rs = fr.read()
            with lk:
                with open(dst, 'a') as fw:
                    fw.write(rs)
            for r in rs.split('\n')[:-1]:
                v1, r, v2, _ = r.split('\t')
                if fn_tm < tr_tm:
                    with lk:
                        tr.add((v1, r, v2))
                elif fn_tm < vd_tm:
                    with lk:
                        vd.add((v1, r, v2))
                else:
                    with lk:
                        ts.add((v1, r, v2))


def split():
    lk = Lock()
    tr, vd, ts = set(), set(), set()
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    for i in range(0, trd_cnt):
        t = Thread(target=_split, args=(tr, vd, ts, lk, trd_cnt, i))
        t.start()
        t.join()
    return tr, vd, ts


def _build(tr, vd, ts, tp, lk, trd_cnt, prt):
    for i, (v1, r, v2) in enumerate(tr):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/train_s.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\n')
        with lk:
            if r == tp:
                with open('./data/split/train_u.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\n')

    for i, (v1, r, v2) in enumerate(vd):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/valid_s.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\n')
        with lk:
            if r == tp:
                with open('./data/split/valid_u.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\n')

    for i, (v1, r, v2) in enumerate(ts):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/test_s.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\n')
        with lk:
            if r == tp:
                with open('./data/split/test_u.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\n')


def build(tr, vd, ts):
    lk = Lock()
    tp = os.getenv('TP', 'U_SE_C_I')
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(tr, vd, ts, tp, lk, trd_cnt, i))
        t.start()
        t.join()


def main():
    tr, vd, ts = split()
    build(tr, vd, ts)


if __name__ == '__main__':
    main()
    exit(0)
