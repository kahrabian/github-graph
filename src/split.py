import glob
import random
import os

from datetime import datetime
from threading import Lock, Thread


def _split(all_d, all_s, of_d, mk_of_d, of_s, mk_of_s, tps, lk, trd_cnt, prt):
    sd = 'graph' if os.getenv('MD', 'G') == 'G' else 'sample'
    for fn in glob.glob(f'./data/{sd}/*.txt'):
        with open(fn, 'r') as fr:
            rs = fr.read()
            for r in rs.split('\n')[:-1]:
                v1, r, v2, t = r.split('\t')
                with lk:
                    all_d.add((v1, r, v2, t))
                with lk:
                    all_s.add((v1, r, v2))
                if r in tps:
                    with lk:
                        if (r, v2, t) not in mk_of_d:
                            of_d.add((v1, r, v2, t))
                            mk_of_d.add((r, v2, t))
                    with lk:
                        if (r, v2) not in mk_of_s:
                            of_s.add((v1, r, v2))
                            mk_of_s.add((r, v2))


def split():
    lk = Lock()
    all_d, all_s, of_d, mk_of_d, of_s, mk_of_s = set(), set(), set(), set(), set(), set()
    tps = os.getenv('TPS', 'U_SE_C_I').split(',')
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_split, args=(all_d, all_s, of_d, mk_of_d, of_s, mk_of_s, tps, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    return list(all_d), list(all_s), list(of_d), list(of_s), list(all_d - of_d), list(all_s - of_s)


def _build(all_d, all_s, of_d, of_s, tr_d, tr_s, lk, trd_cnt, prt):
    for i, (v1, r, v2, t) in enumerate(all_d):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/all_d.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')
    for i, (v1, r, v2, t) in enumerate(of_d):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/of_d.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')
    for i, (v1, r, v2, t) in enumerate(tr_d):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/train_d.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')
    for i, (v1, r, v2, t) in enumerate(of_d):
        if i % trd_cnt != prt:
            continue
        if i % 10 < 8:
            with lk:
                with open('./data/split/train_d.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')
        elif i % 10 == 8:
            with lk:
                with open('./data/split/valid_d.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')
        else:
            with lk:
                with open('./data/split/test_d.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')

    for i, (v1, r, v2) in enumerate(all_s):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/all_s.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\n')
    for i, (v1, r, v2) in enumerate(of_s):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/of_s.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\n')
    for i, (v1, r, v2) in enumerate(tr_s):
        if i % trd_cnt != prt:
            continue
        with lk:
            with open('./data/split/train_s.txt', 'a') as fw:
                fw.write(f'{v1}\t{r}\t{v2}\n')
    for i, (v1, r, v2) in enumerate(of_s):
        if i % trd_cnt != prt:
            continue
        if i % 10 < 8:
            with lk:
                with open('./data/split/train_s.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\n')
        elif i % 10 == 8:
            with lk:
                with open('./data/split/valid_s.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\n')
        else:
            with lk:
                with open('./data/split/test_s.txt', 'a') as fw:
                    fw.write(f'{v1}\t{r}\t{v2}\n')


def build(all_d, all_s, of_d, of_s, tr_d, tr_s):
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(all_d, all_s, of_d, of_s, tr_d, tr_s, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


def main():
    all_d, all_s, of_d, of_s, tr_d, tr_s = split()
    build(all_d, all_s, of_d, of_s, tr_d, tr_s)


if __name__ == '__main__':
    random.seed(2019)
    main()
    exit(0)
