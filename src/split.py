import glob
import random
import os

from datetime import datetime
from threading import Lock, Thread


def _format(r):
    tr = os.getenv('TR', 'H')
    if tr == 'H':
        return list(map(lambda x: (x[1], *x[0]), r.items()))
    elif tr == 'T':
        return list(map(lambda x: (x[0][0], x[1], *x[0][1:]), r.items()))
    elif tr == 'B':
        return list(map(lambda x: (x[1], *x[0][1:]), filter(lambda x: x[0][0] == 'H', r.items())))


def _extract(nr_t, nr_s, r_t, r_s, es, rs, tps, lk, trd_cnt, prt):
    sd = 'graph' if os.getenv('MD', 'G') == 'G' else 'sample'
    tr = os.getenv('TR', 'H')
    for fn in glob.glob(f'./data/{sd}/*.txt'):
        fn_tm = datetime.strptime(fn, f'./data/{sd}/%Y-%m-%d-%H.txt')
        if fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                r = l.strip()
                if r == '':
                    continue
                v1, v2, r, t = r.split('\t')
                t = int(datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ').timestamp())
                if r in tps:
                    with lk:
                        if tr == 'H' and (v2, r, t) not in r_t:
                            r_t[(v2, r, t)] = v1
                        if tr == 'T' and (v1, r, t) not in r_t:
                            r_t[(v1, r, t)] = v2
                        if tr == 'B' and ('H', v2, r, t) not in r_t and (v1, 'T', r, t) not in r_t:
                            r_t[('H', v2, r, t)] = v1
                            r_t[(v1, 'T', r, t)] = v2
                    with lk:
                        if tr == 'H' and (v2, r) not in r_s:
                            r_s[(v2, r)] = v1
                        if tr == 'T' and (v1, r) not in r_s:
                            r_s[(v1, r)] = v2
                        if tr == 'B' and ('H', v2, r) not in r_s and (v1, 'T', r) not in r_s:
                            r_s[('H', v2, r)] = v1
                            r_s[(v1, 'T', r)] = v2
                else:
                    nr_t[(v1, v2, r, t)] = True
                    nr_s[(v1, v2, r)] = True
                with lk:
                    es[v1] = True
                    es[v2] = True
                with lk:
                    rs[r] = True


def extract():
    lk = Lock()
    nr_t, nr_s, r_t, r_s, es, rs = {}, {}, {}, {}, {}, {}
    tps = os.getenv('TPS', 'U_SE_C_I').split(',')
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_extract, args=(nr_t, nr_s, r_t, r_s, es, rs, tps, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    r_t = _format(r_t)
    r_s = _format(r_s)
    return list(nr_t.keys()), list(nr_s.keys()), r_t, r_s, es.keys(), rs.keys()


def index(s, fn):
    idx = {x: i for i, x in enumerate(s)}
    with open(f'{t_pth}/{fn}.txt', 'a') as f:
        f.write(f'{len(idx)}\n')
    with open(f'{s_pth}/{fn}.txt', 'a') as f:
        f.write(f'{len(idx)}\n')
    with open(f'{t_pth}/{fn}.txt', 'a') as ft, open(f'{s_pth}/{fn}.txt', 'a') as fs:
        for x, i in idx.items():
            ft.write(f'{x}\t{i}\n')
            fs.write(f'{x}\t{i}\n')
    return idx


def _split(r, ln, sz):
    return r[:int(ln * sz)], r[int(ln * sz):int(ln * (sz + (1 - sz) / 2))], r[int(ln * (sz + (1 - sz) / 2)):]


def split(nr, r, pth):
    random.shuffle(r)
    tr_r, vd, ts = _split(r, len(r), 0.8)
    tr = nr + tr_r
    random.shuffle(tr)
    random.shuffle(vd)
    random.shuffle(ts)

    with open(f'{pth}/train2id.txt', 'a') as f:
        f.write(f'{len(tr)}\n')
    with open(f'{pth}/valid2id.txt', 'a') as f:
        f.write(f'{len(vd)}\n')
    with open(f'{pth}/test2id.txt', 'a') as f:
        f.write(f'{len(ts)}\n')

    return tr, vd, ts


def _write(x, pth, fn, e_idx, r_idx, lk, trd_cnt, prt):
    with open(f'{pth}/{fn}.txt', 'a') as fw:
        for i, x in enumerate(x):
            if i % trd_cnt != prt:
                continue
            with lk:
                if len(x) == 4:
                    fw.write(f'{e_idx[x[0]]}\t{e_idx[x[1]]}\t{r_idx[x[2]]}\t{x[3]}\n')
                else:
                    fw.write(f'{e_idx[x[0]]}\t{e_idx[x[1]]}\t{r_idx[x[2]]}\n')


def _build(tr, vd, ts, pth, e_idx, r_idx, lk, trd_cnt, prt):
    _write(tr, pth, 'train2id', e_idx, r_idx, lk, trd_cnt, prt)
    _write(vd, pth, 'valid2id', e_idx, r_idx, lk, trd_cnt, prt)
    _write(ts, pth, 'test2id', e_idx, r_idx, lk, trd_cnt, prt)


def build(tr, vd, ts, pth, e_idx, r_idx):
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    _ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(tr, vd, ts, pth, e_idx, r_idx, lk, trd_cnt, i))
        t.start()
        _ts.append(t)
    for t in _ts:
        t.join()


def main():
    nr_t, nr_s, r_t, r_s, es, rs = extract()
    e_idx = index(es, 'entity2id')
    r_idx = index(rs, 'relation2id')
    tr_t, vd_t, ts_t = split(nr_t, r_t, t_pth)
    tr_s, vd_s, ts_s = split(nr_s, r_s, s_pth)
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
