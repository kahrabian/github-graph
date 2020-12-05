import glob
import json
import os
import pickle
import re
from datetime import datetime
from queue import Queue
from threading import Lock, Thread


def _graph(g, lk, trd_cnt, prt):
    for fn in glob.glob('./data/all_all/*.txt'):
        if datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.txt').toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as f:
            for l in f.readlines():
                tup = l.strip().split('\t')
                if tup[2] in ['U_W_R', 'U_P_R', 'U_A_R']:
                    continue
                with lk:
                    if tup[0] not in g:
                        g[tup[0]] = set()
                    g[tup[0]].add(tup[2])
                with lk:
                    if tup[2] not in g:
                        g[tup[2]] = set()
                    g[tup[2]].add(tup[0])


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


def _build(tups, vs, lk, trd_cnt, prt):
    _tups = []
    for fn in glob.glob('./data/all_all/*.txt'):
        fn_tm = datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.txt')
        if fn_tm.toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                tup = l.strip().split('\t')
                if tup[0] in vs and tup[2] in vs:
                    _tups.append((tup[0], tup[1], tup[2], tup[3]))
    with lk:
        tups += _tups


def build(vs, trd_cnt):
    tups, ts = [], []
    lk = Lock()
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(tups, vs, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    return tups


def load(fn):
    with open(fn, 'rb') as f:
        p = pickle.load(f)
    return p


def dump(fn, x):
    with open(fn, 'wb') as f:
        pickle.dump(x, f)


def extract(tups, prj):
    dm, pr_r, c_prs = {}, {}, set()
    for s, r, o, t in tups:
        t = datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
        if (t.year - 2015) * 12 + t.month not in dm:
            dm[(t.year - 2015) * 12 + t.month] = []
        dm[(t.year - 2015) * 12 + t.month].append((s, r, o, int(t.timestamp())))

        if r in ['P_O_R', 'P_C_R']:
            pr_r[s] = o

        if r == 'U_C_P':
            c_prs.add((s, r, o, int(t.timestamp())))
    print(len(dm.keys()), list(map(len, dm.values())), prj)

    x = []
    for i in range(1, 60):
        if i not in dm:
            print(i, prj)
            continue
        cont, cont_r, intg, intg_r = {}, {}, {}, {}
        x += dm[i]
        for z in x + dm[i + 1]:
            if z[1] == 'U_O_P' and z[2] in pr_r:
                cont[z[2]] = z[0]
                if z[0] not in cont_r:
                    cont_r[z[0]] = set()
                cont_r[z[0]].add(z[2])

        for z in x:
            if z[1] == 'U_C_P' and z[2] in pr_r and z[2] in cont and z[0] != cont[z[2]]:
                if pr_r[z[2]] not in intg:
                    intg[pr_r[z[2]]] = set()
                intg[pr_r[z[2]]].add(z[0])
                if z[0] not in intg_r:
                    intg_r[z[0]] = set()
                intg_r[z[0]].add((z[3], z[2]))
        if len(intg) == 0:
            print('empty intg:', i)

        o_prs = {}
        for z in dm[i + 1]:
            if z[1] == 'U_O_P' and z[2] in pr_r:
                o_prs[z[2]] = (z[0], z[3])

        pr_integrator_space = {}
        y, y_2, y_extra = [], [], []
        for z in c_prs:
            if z[2] in o_prs and z[0] != o_prs[z[2]][0] and z[2] in pr_r and pr_r[z[2]] in intg and z[0] in intg[pr_r[z[2]]]:
                y.append((z[0], z[1], z[2], o_prs[z[2]][1]))
                y_2.append((z[0], z[2], o_prs[z[2]][0], o_prs[z[2]][1]))
                y_extra.append((z[2], 'P_O_R', pr_r[z[2]], o_prs[z[2]][1]))
                y_extra.append((o_prs[z[2]][0], 'U_O_P', z[2], o_prs[z[2]][1]))
                pr_integrator_space[z[2]] = list(intg[pr_r[z[2]]])

        o_prs = {}
        for z in x:
            if z[1] == 'U_O_P' and z[2] in pr_r:
                o_prs[z[2]] = (z[0], z[3])

        x_2 = []
        for z in c_prs:
            if z[2] in o_prs and z[0] != o_prs[z[2]][0] and z[2] in pr_r and pr_r[z[2]] in intg and z[0] in intg[pr_r[z[2]]]:
                x_2.append((z[0], z[2], o_prs[z[2]][0], o_prs[z[2]][1]))
                pr_integrator_space[z[2]] = list(intg[pr_r[z[2]]])

        p = f'./_data/processed/{prj}/{i}'
        os.makedirs(p, exist_ok=True)
        print(p, len(x), len(x_2), len(y), len(y_2), [len(intg[k]) for k in intg])

        with open(f'{p}/train.txt', 'w') as f:
            for (s, r, o, t) in x:
                f.write(f'{s}\t{r}\t{o}\t{t}\n')
        with open(f'{p}/train_2.txt', 'w') as f:
            for (i, pr, c, t) in x_2:
                f.write(f'{i}\t{pr}\t{c}\t{t}\n')
        with open(f'{p}/test.txt', 'w') as f:
            for (s, r, o, t) in y:
                f.write(f'{s}\t{r}\t{o}\t{t}\n')
        with open(f'{p}/test_2.txt', 'w') as f:
            for (i, pr, c, t) in y_2:
                f.write(f'{i}\t{pr}\t{c}\t{t}\n')
        with open(f'{p}/test_extra.txt', 'w') as f:
            for (s, r, o, t) in y_extra:
                f.write(f'{s}\t{r}\t{o}\t{t}\n')
        with open(f'{p}/pr_integrator_space.dict', 'w') as f:
            f.write(json.dumps(pr_integrator_space))
        with open(f'{p}/pr_integrator.dict', 'w') as f:
            f.write(json.dumps({k: list(v) for k, v in intg_r.items()}))
        with open(f'{p}/integrator.dict', 'w') as f:
            f.write(json.dumps({k: i for i, k in enumerate(intg_r.keys())}))
        with open(f'{p}/pr_contributor.dict', 'w') as f:
            f.write(json.dumps({k: list(v) for k, v in cont_r.items()}))
        with open(f'{p}/contributor.dict', 'w') as f:
            f.write(json.dumps(cont))


if __name__ == '__main__':
    trd_cnt = int(os.getenv('TRD_CNT', '16'))

    g_p = './_data/tmp/g.pkl'
    if os.path.exists(g_p):
        g = load(g_p)
    else:
        g = graph(trd_cnt)
        dump(g_p, g)
    print(f'graph size: {len(g)}')

    roots = {
        '/repo/20580498': 'kubernetes/kubernetes',
        '/repo/3638964': 'ansible/ansible',
        '/repo/2310495': 'ceph/ceph',
        '/repo/3234987': 'tgstation/tgstation',
    }
    for fn, v in roots.items():
        p = fn.replace('/', '_')
        vs_p = f'./_data/tmp/vs_{p}.pkl'
        if os.path.exists(vs_p):
            vs = load(vs_p)
        else:
            vs = bfs(g, v)
            dump(vs_p, vs)
        print(f'sample node size {p}: {len(vs)}')

        tups = build(vs, trd_cnt)
        extract(tups, p)
