import glob
import json
import os
import pickle
from datetime import datetime
from threading import Lock, Thread


def _build(tups, vs, lk, trd_cnt, prt):
    _tups = []
    for fn in glob.glob('./data/all_all/*.txt'):
        fn_tm = datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.txt')
        if fn_tm.toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                tup = l.strip().split('\t')
                if tup[1] not in ['P_R', 'I_R'] and tup[0] in vs and tup[2] in vs:
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


def extract(tups, prj):
    dm, c_prs = {}, set()
    for s, r, o, t in tups:
        t = datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
        m = (t.year - 2015) * 12 + t.month
        if m not in dm:
            dm[m] = []
        dm[m].append((s, r, o, int(t.timestamp())))

        if r == 'U_C_P':
            c_prs.add((s, r, o, int(t.timestamp())))

    x = []
    for i in range(1, 60):
        if i not in dm:
            continue
        cont, intg = {}, {}
        x += dm[i]
        for z in x + dm[i + 1]:
            if z[1] == 'U_O_P':
                cont[z[2]] = z[0]

        for z in x:
            if z[1] == 'U_C_P' and z[0] != cont.get(z[2], ''):
                intg.add(z[0])

        o_prs = {}
        for z in dm[i + 1]:
            if z[1] == 'U_O_P':
                o_prs[z[2]] = z

        y, y_extra = [], []
        for z in c_prs:
            if z[2] in o_prs and z[0] != o_prs[z[2]][0] and z[0] in intg:
                y.append(z)
                y_extra.append(o_prs[z[2]])

        p = f'./data/processed/{prj}/{i}'
        os.makedirs(p, exist_ok=True)
        with open(f'{p}/train.txt', 'w') as f:
            for (s, r, o, t) in x:
                f.write(f'{s}\t{r}\t{o}\t{t}\n')
        with open(f'{p}/test.txt', 'w') as f:
            for (s, r, o, t) in y:
                f.write(f'{s}\t{r}\t{o}\t{t}\n')
        with open(f'{p}/test_extra.txt', 'w') as f:
            for (s, r, o, t) in y_extra:
                f.write(f'{s}\t{r}\t{o}\t{t}\n')
        with open(f'{p}/integrator_space.dict', 'w') as f:
            f.write(json.dumps(list(intg)))


if __name__ == '__main__':
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    for fn in ['kubernetes_kubernetes', 'ansible_ansible', 'ceph_ceph', 'tgstation_tgstation']:
        vs = load(f'./data/tmp/vs_{fn}.pkl')
        tups = build(vs, trd_cnt)
        extract(tups, fn)
