import glob
import random
import os

from datetime import datetime
from threading import Lock, Thread


def _unique(q_r, static=False):
    ru, mk = [], {}
    tr = os.getenv('TR', 'H')
    for (v1, v2, r, t) in q_r:
        if static:
            if tr == 'H' and (v2, r) not in mk:
                mk[(v2, r)] = True
                ru.append((v1, v2, r, t))
            if tr == 'T' and (v1, r) not in mk:
                mk[(v1, r)] = True
                ru.append((v1, v2, r, t))
            if tr == 'B' and ('H', v2, r) not in mk and (v1, 'T', r) not in mk:
                mk[('H', v2, r)] = True
                mk[(v1, 'T', r)] = True
                ru.append((v1, v2, r, t))
        else:
            if tr == 'H' and (v2, r, t) not in mk:
                mk[(v2, r, t)] = True
                ru.append((v1, v2, r, t))
            elif tr == 'T' and (v1, r, t) not in mk:
                mk[(v1, r, t)] = True
                ru.append((v1, v2, r, t))
            elif tr == 'B' and ('H', v2, r, t) not in mk and (v1, 'T', r, t) not in mk:
                mk[('H', v2, r, t)] = True
                mk[(v1, 'T', r, t)] = True
                ru.append((v1, v2, r, t))
    return ru


def _extract(q_nr, q_r, es, rs, tps, lk, trd_cnt, prt):
    sd = 'graph' if os.getenv('MD', 'G') == 'G' else 'sample'
    for fn in glob.glob(f'./data/{sd}/*.txt'):
        fn_tm = datetime.strptime(fn, f'./data/{sd}/%Y-%m-%d-%H.txt')
        if fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                l = l.strip()
                if l == '':
                    continue
                v1, v2, r, t = l.split('\t')
                t = int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp())
                if r in tps:
                    with lk:
                        q_r.append((v1, v2, r, t))
                else:
                    with lk:
                        q_nr.append((v1, v2, r, t))
                with lk:
                    es[v1] = True
                    es[v2] = True
                with lk:
                    rs[r] = True


def extract():
    lk = Lock()
    q_nr, q_r, es, rs = [], [], {}, {}
    tps = os.getenv('TPS', 'U_SE_C_I').split(',')
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_extract, args=(q_nr, q_r, es, rs, tps, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    q_rt = _unique(q_r)
    q_rs = _unique(q_r, static=True)
    return q_nr, q_rt, q_rs, es.keys(), rs.keys()


def index(s, fn):
    idx = {x: i for i, x in enumerate(s)}
    with open(f'{t_pth}/{fn}.dict', 'a') as ft, open(f'{s_pth}/{fn}.dict', 'a') as fs:
        for x, i in idx.items():
            ft.write(f'{i}\t{x}\n')
            fs.write(f'{i}\t{x}\n')
    return idx


def _split_interpolation(r, ln, sz):
    return r[:int(ln * sz)], r[int(ln * sz):int(ln * (sz + (1 - sz) / 2))], r[int(ln * (sz + (1 - sz) / 2)):]


def _split_extrapolation(q_r, sz, static=False):
    t = list(map(lambda x: x[3], q_r))
    lb_t, ub_t = min(t), max(t)
    t_tr = lb_t + sz * (ub_t - lb_t)
    t_vd = t_tr + ((1 - sz) / 2) * (ub_t - lb_t)

    tr = list(filter(lambda x: x[3] < t_tr, q_r))
    vd = list(filter(lambda x: t_tr <= x[3] < t_vd, q_r))
    ts = list(filter(lambda x: t_vd <= x[3], q_r))

    if static:
        tr = list(map(lambda x: x[:3], tr))
        vd = list(map(lambda x: x[:3], vd))
        ts = list(map(lambda x: x[:3], ts))

    return tr, vd, ts


def split(q_nr, q_r, pth, static=False):
    random.shuffle(q_r)
    if os.getenv('SP', 'I') == 'I':
        tr_r, vd, ts = _split_interpolation(q_r, len(q_r), 0.8)
        tr = q_nr + tr_r
    else:
        tr, vd, ts = _split_extrapolation(q_nr + q_r, 0.8, static=static)
    random.shuffle(tr)
    random.shuffle(vd)
    random.shuffle(ts)

    return tr, vd, ts


def _write(x, pth, fn, lk, trd_cnt, prt):
    with open(f'{pth}/{fn}.txt', 'a') as f:
        for i, x in enumerate(x):
            if i % trd_cnt != prt:
                continue
            if len(x) == 4:
                with lk:
                    f.write(f'{x[0]}\t{x[2]}\t{x[1]}\t{x[3]}\n')
            else:
                with lk:
                    f.write(f'{x[0]}\t{x[2]}\t{x[1]}\n')


def _build(tr, vd, ts, pth, lk, trd_cnt, prt):
    _write(tr, pth, 'train', lk, trd_cnt, prt)
    _write(vd, pth, 'valid', lk, trd_cnt, prt)
    _write(ts, pth, 'test', lk, trd_cnt, prt)


def build(tr, vd, ts, pth, e_idx, r_idx):
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    _ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(tr, vd, ts, pth, lk, trd_cnt, i))
        t.start()
        _ts.append(t)
    for t in _ts:
        t.join()


def main():
    q_nr, q_rt, q_rs, es, rs = extract()
    e_idx = index(es, 'entities')
    r_idx = index(rs, 'relations')
    tr_t, vd_t, ts_t = split(q_nr, q_rt, t_pth)
    tr_s, vd_s, ts_s = split(q_nr, q_rs, s_pth, static=True)
    build(tr_t, vd_t, ts_t, t_pth, e_idx, r_idx)
    build(tr_s, vd_s, ts_s, s_pth, e_idx, r_idx)


if __name__ == '__main__':
    random.seed(2020)

    t_pth = './data/split/temporal'
    if not os.path.isdir(t_pth):
        os.mkdir(t_pth)

    s_pth = './data/split/static'
    if not os.path.isdir(s_pth):
        os.mkdir(s_pth)

    main()
