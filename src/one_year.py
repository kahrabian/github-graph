import glob
import os
import pickle
import re
from datetime import datetime
from queue import Queue
from threading import Lock, Thread


def _graph(g, lk, trd_cnt, prt):
    for fn in glob.glob('./data/graph/*.txt'):
        if datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt').toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as f:
            for l in f.readlines():
                v1, v2, r, _ = l.split('\t')
                with lk:
                    if v1 not in g:
                        g[v1] = set()
                    g[v1].add(v2)
                with lk:
                    if v2 not in g:
                        g[v2] = set()
                    g[v2].add(v1)


def graph(trd_cnt):
    g = {}
    lk = Lock()
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_graph, args=(g, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    return g


def bfs(g, root):
    vs = set()  # NOTE: Mark
    vs.add(root)

    q = Queue()
    q.put(root)
    while not q.empty():
        v = q.get()
        for u in g[v] - vs:
            if re.match('\/(.*?)\/', u).groups()[0] != 'user':
                q.put(u)
            vs.add(u)
    return vs


def _build(vs, p, trd_cnt, prt):
    for fn in glob.glob('./data/graph/*.txt'):
        fn_tm = datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt')
        inc_pth = fn_tm.strftime(f'./data/{p}/%Y-%m-%d-%H_.txt')
        com_pth = fn_tm.strftime(f'./data/{p}/%Y-%m-%d-%H.txt')
        if os.path.exists(com_pth) or fn_tm.toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            with open(inc_pth, 'w') as fw:
                for l in fr.readlines():
                    v1, v2, r, t = l.strip().split('\t')
                    if v1 in vs and v2 in vs:
                        fw.write(f'{v1}\t{r}\t{v2}\t{t}\n')
        os.rename(inc_pth, com_pth)


def build(vs, p, trd_cnt):
    os.makedirs(f'./data/{p}', exist_ok=True)

    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(vs, p, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


def load(fn):
    with open(fn, 'rb') as f:
        p = pickle.load(f)
    return p


def dump(fn, x):
    with open(fn, 'wb') as f:
        pickle.dump(x, f)


if __name__ == '__main__':
    trd_cnt = int(os.getenv('TRD_CNT', '16'))

    g_p = './data/tmp/g.pkl'
    if os.path.exists(g_p):
        g = load(g_p)
    else:
        g = graph(trd_cnt)
        dump(g_p, g)
    print(f'graph size: {len(g)}')

    for i, v in enumerate(g.keys()):
        if re.match('\/(.*?)\/', v).groups()[0] != 'repo':
            continue
        p = v.split('/')[-1]
        vs_p = f'./data/tmp/vs_{p}.pkl'
        if os.path.exists(vs_p):
            vs = load(vs_p)
        else:
            vs = bfs(g, v)
            dump(vs_p, vs)
        print(f'[{i}], sample node size {p}: {len(vs)}')

        build(vs, p, trd_cnt)