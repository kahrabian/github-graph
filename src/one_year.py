import glob
import os
import pickle
import re
from datetime import datetime
from queue import Queue
from threading import Lock, Thread


def _graph(g, lk, trd_cnt, prt):
    for fn in glob.glob('./data/graph/*/*.txt'):
        if datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.txt').toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as f:
            for l in f.readlines():
                tup = l.strip().split('\t')
                with lk:
                    if tup[0] not in g:
                        g[tup[0]] = set()
                    g[tup[0]].add(tup[1])
                with lk:
                    if tup[1] not in g:
                        g[tup[1]] = set()
                    g[tup[1]].add(tup[0])


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
            if re.match('\/(.*?)\/', u).groups()[0] not in ['user', 'repo']:
                q.put(u)
            vs.add(u)
    return vs


def _build(vs, p, trd_cnt, prt):
    for fn in glob.glob('./data/graph/*/*.txt'):
        fn_tm = datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.txt')
        inc_pth = fn_tm.strftime(f'./data/{p}/%Y-%m-%d-%H_.txt')
        com_pth = fn_tm.strftime(f'./data/{p}/%Y-%m-%d-%H.txt')
        if os.path.exists(com_pth) or fn_tm.toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            with open(inc_pth, 'w') as fw:
                for l in fr.readlines():
                    tup = l.strip().split('\t')
                    if tup[0] in vs and tup[1] in vs:
                        fw.write(f'{tup[0]}\t{tup[2]}\t{tup[1]}\t{tup[3]}\n')
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

    _vs = set()
    roots = {
        'kubernetes/kubernetes': '/repo/20580498',
        'ansible/ansible': '/repo/3638964',
        # 'elastic/kibana': '/repo/7833168',
        'ceph/ceph': '/repo/2310495',
        # 'apple/swift': '/repo/44838949',
        'tgstation/tgstation': '/repo/3234987',
        # 'rust-lang/rust': '/repo/724712',
        # 'elastic/elasticsearch': '/repo/507775',
        # 'apache/spark': '/repo/17165658',
        # 'dotnet/corefx': '/repo/26295345',
        # 'saltstack/salt': '/repo/1390248',
        # 'cockroachdb/cockroach': '/repo/16563587',
        # 'dimagi/commcare-hq': '/repo/247278',
        # 'cms-sw/cmssw': '/repo/10969551',
        # 'nodejs/node': '/repo/27193779',
        # 'dotnet/roslyn': '/repo/29078997',
    }
    for fn, v in roots.items():
        p = fn.replace('/', '_')
        vs_p = f'./data/tmp/vs_{p}.pkl'
        if os.path.exists(vs_p):
            vs = load(vs_p)
        else:
            vs = bfs(g, v)
            dump(vs_p, vs)
        _vs = _vs.union(vs)
        print(f'sample node size {p}: {len(vs)}')

    build(_vs, 'all_all', trd_cnt)
