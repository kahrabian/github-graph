import glob
import json
import os
import pickle
import re
from collections import Counter
from datetime import datetime
from queue import Queue
from threading import Lock, Thread


def _graph(g, year, lk, trd_cnt, prt):
    for fn in glob.glob(f'./data/graph/{year}/*.txt'):
        if datetime.strptime(fn, f'./data/graph/{year}/%Y-%m-%d-%H.txt').toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as f:
            for l in f.readlines():
                tup = l.split('\t')
                with lk:
                    if tup[0] not in g:
                        g[tup[0]] = set()
                    g[tup[0]].add(tup[1])
                with lk:
                    if tup[1] not in g:
                        g[tup[1]] = set()
                    g[tup[1]].add(tup[0])


def graph(trd_cnt, year):
    g = {}
    lk = Lock()
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_graph, args=(g, year, lk, trd_cnt, i))
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
    return dict(Counter(list(map(lambda x: re.match('\/(.*?)\/', x).groups()[0], vs))))


def load(fn):
    with open(fn, 'rb') as f:
        p = pickle.load(f)
    return p


def dump(fn, x):
    with open(fn, 'wb') as f:
        pickle.dump(x, f)


if __name__ == '__main__':
    year = int(os.getenv('YEAR', '2015'))
    trd_cnt = int(os.getenv('TRD_CNT', '1'))
    total_jobs = int(os.getenv('TOTAL_JOBS', '1'))
    task_id = int(os.getenv('SLURM_ARRAY_TASK_ID', '0'))

    g_p = f'./data/tmp/g_{year}.pkl'
    if os.path.exists(g_p):
        g = load(g_p)
    else:
        g = graph(trd_cnt, year)
        dump(g_p, g)
    print(f'graph size: {len(g)}')

    info = {}
    repos = list(sorted(filter(lambda x: re.match('\/(.*?)\/', x).groups()[0] == 'repo', g.keys())))
    for i, v in enumerate(repos):
        if i % total_jobs != task_id:
            continue
        info[v] = bfs(g, v)
        if (i + 1) % 10 ** 5 == 0:
            print(f'[{i + 1}/{len(repos)}] done')

    with open(f'./data/tmp/info_{year}_{task_id}.json', 'w') as f:
        f.write(json.dumps(info))
