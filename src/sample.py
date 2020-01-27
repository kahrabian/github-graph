import glob
import random
import os

from datetime import datetime
from queue import PriorityQueue
from threading import Lock, Thread


def _extract(g, lk, trd_cnt, prt):
    st_tm = datetime.strptime(os.getenv('ST_TM', ''), '%Y-%m-%d-%H')
    sp_tm = datetime.strptime(os.getenv('SP_TM', ''), '%Y-%m-%d-%H')
    for fn in glob.glob('./data/graph/*.txt'):
        fn_tm = datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.hour % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                v1, r, v2, t = l.split('\t')
                with lk:
                    if v1 not in g:
                        g[v1] = set()
                    g[v1].add(v2)

                    # NOTE: To find nodes with the most interactions
                    if v2 not in g:
                        g[v2] = set()
                    g[v2].add(v1)


def extract():
    g = {}
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    for i in range(0, trd_cnt):
        t = Thread(target=_extract, args=(g, lk, trd_cnt, i))
        t.start()
        t.join()
    return g


def _sample(g, in_sz, tg_sz, smpl_rt):
    mk = set()
    q = PriorityQueue()
    for _, v in sorted(map(lambda x: (len(x[1]), x[0]), g.items()), reverse=True)[:in_sz]:
        mk.add(v)
        q.put((-len(g[v]), v))

    vs = set()
    while not q.empty() and len(vs) < tg_sz:
        _, v = q.get()
        vs.add(v)

        ss = g.get(v, set()) - mk
        for n in random.sample(ss, min(len(ss), smpl_rt)):
            mk.add(n)
            q.put((-len(g.get(n, [])), n))
    return vs


def sample(g):
    in_sz = int(os.getenv('IN_SZ', '100'))
    tg_sz = int(os.getenv('TG_SZ', '10000'))
    smpl_rt = int(os.getenv('SMPL_RT', '100'))
    vs = _sample(g, in_sz, tg_sz, smpl_rt)
    return vs


def _build(vs, trd_cnt, prt):
    st_tm = datetime.strptime(os.getenv('ST_TM', ''), '%Y-%m-%d-%H')
    sp_tm = datetime.strptime(os.getenv('SP_TM', ''), '%Y-%m-%d-%H')
    for fn in glob.glob('./data/graph/*.txt'):
        fn_tm = datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt')
        inc_pth = fn_tm.strftime('./data/sample/_%Y-%m-%d-%H.txt')
        com_pth = fn_tm.strftime('./data/sample/%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.hour % trd_cnt != prt or os.path.exists(com_pth):
            continue
        with open(fn, 'r') as fr:
            with open(inc_pth, 'w') as fw:
                for l in fr.readlines():
                    v1, _, v2, _ = l.split('\t')
                    if v1 in vs and v2 in vs:
                        fw.write(l)
        os.rename(inc_pth, com_pth)


def build(vs):
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(vs, trd_cnt, i))
        t.start()
        t.join()


def main():
    g = extract()
    vs = sample(g)
    build(vs)


if __name__ == '__main__':
    main()
    exit(0)
