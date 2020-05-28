import glob
import random
import os
from datetime import datetime
from threading import Lock, Thread


def _extract(q_nr, q_r, es, rs, tps, lk, trd_cnt, prt):
    for fn in glob.glob(f'./data/{os.getenv("DIR", "graph")}/*.txt'):
        if datetime.strptime(fn, f'./data/{os.getenv("DIR", "graph")}/%Y-%m-%d-%H.txt').toordinal() % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                l = l.strip()
                if l == '':
                    continue
                v1, r, v2, t = l.strip().split('\t')
                t = int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp())
                if r in tps:
                    with lk:
                        q_r.append((v1, r, v2, t))
                else:
                    with lk:
                        q_nr.append((v1, r, v2, t))
                with lk:
                    es[v1] = True
                    es[v2] = True
                with lk:
                    rs[r] = True


def extract():
    lk = Lock()
    q_nr, q_r, es, rs = [], [], {}, {}
    tps = os.getenv('TPS', '').split(',')
    trd_cnt = int(os.getenv('TRD_CNT', '1'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_extract, args=(q_nr, q_r, es, rs, tps, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    return q_nr, q_r, es.keys(), rs.keys()


def index(s, fn):
    idx = {x: i for i, x in enumerate(s)}
    with open(f'{pth}/{fn}.dict', 'a') as f:
        for x, i in idx.items():
            f.write(f'{i}\t{x}\n')
    return idx


def _split_interpolation(r, ln, sz):
    return r[:int(ln * sz)], r[int(ln * sz):int(ln * (sz + (1 - sz) / 2))], r[int(ln * (sz + (1 - sz) / 2)):]


def _split_extrapolation(q_r, sz):
    t = list(map(lambda x: x[3], q_r))
    lb_t, ub_t = min(t), max(t)
    t_tr = lb_t + sz * (ub_t - lb_t)
    t_vd = t_tr + ((1 - sz) / 2) * (ub_t - lb_t)

    tr = list(filter(lambda x: x[3] < t_tr, q_r))
    vd = list(filter(lambda x: t_tr <= x[3] < t_vd, q_r))
    ts = list(filter(lambda x: t_vd <= x[3], q_r))

    return tr, vd, ts


def split(q_nr, q_r):
    random.shuffle(q_r)
    if os.getenv('SP', 'I') == 'I':
        tr_r, vd, ts = _split_interpolation(q_r, len(q_r), 0.9)
        tr = q_nr + tr_r
    else:
        tr, vd, ts = _split_extrapolation(q_nr + q_r, 0.9)
    random.shuffle(tr)
    random.shuffle(vd)
    random.shuffle(ts)

    return tr, vd, ts


def _write(x, pth, fn, lk, trd_cnt, prt):
    with open(f'{pth}/{fn}.txt', 'a') as f:
        for i, x in enumerate(x):
            if i % trd_cnt != prt:
                continue
            with lk:
                f.write('\t'.join(map(str, x)) + '\n')


def _build(tr, vd, ts, pth, lk, trd_cnt, prt):
    _write(tr, pth, 'train', lk, trd_cnt, prt)
    _write(vd, pth, 'valid', lk, trd_cnt, prt)
    _write(ts, pth, 'test', lk, trd_cnt, prt)


def build(tr, vd, ts, pth, e_idx, r_idx):
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '1'))
    _ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(tr, vd, ts, pth, lk, trd_cnt, i))
        t.start()
        _ts.append(t)
    for t in _ts:
        t.join()


def main():
    q_nr, q_r, es, rs = extract()
    e_idx = index(es, 'entities')
    r_idx = index(rs, 'relations')
    tr, vd, ts = split(q_nr, q_r)
    build(tr, vd, ts, pth, e_idx, r_idx)


if __name__ == '__main__':
    random.seed(2020)

    pth = './data/split'
    if not os.path.isdir(pth):
        os.mkdir(pth)

    main()
