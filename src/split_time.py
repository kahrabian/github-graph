import glob
import os

from datetime import datetime
from threading import Lock, Thread


def _extract(tr, vd, ts, mk_vd, mk_ts, es, rs, tr_tm, vd_tm, ts_dm, st_dm, tps, lk, trd_cnt, prt):
    sd = 'graph' if os.getenv('MD', 'G') == 'G' else 'sample'
    ts_md = os.getenv('TS_MD', 'H')
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
                if tr_tm <= t < vd_tm:
                    tr[(v1, v2, r, t)] = True
                elif vd_tm <= t < ts_dm and r in tps:
                    if ts_md == 'H' and (v2, r) not in mk_vd:
                        mk_vd[(v2, r)] = True
                        vd[(v1, v2, r, t)] = True
                    elif ts_md == 'T' and (v1, r) not in mk_vd:
                        mk_vd[(v2, r)] = True
                        vd[(v1, v2, r, t)] = True
                    elif ts_md == 'B' and ('H', v2, r) not in mk_vd and (v1, 'T', r) not in mk_vd:
                        mk_vd[('H', v2, r)] = True
                        mk_vd[(v1, 'T', r)] = True
                        vd[(v1, v2, r, t)] = True
                elif ts_dm <= t < st_dm and r in tps:
                    if ts_md == 'H' and (v2, r) not in mk_ts:
                        mk_ts[(v2, r)] = True
                        ts[(v1, v2, r, t)] = True
                    elif ts_md == 'T' and (v1, r) not in mk_ts:
                        mk_ts[(v2, r)] = True
                        ts[(v1, v2, r, t)] = True
                    elif ts_md == 'B' and ('H', v2, r) not in mk_ts and (v1, 'T', r) not in mk_ts:
                        mk_ts[('H', v2, r)] = True
                        mk_ts[(v1, 'T', r)] = True
                        ts[(v1, v2, r, t)] = True
                else:
                    continue

                with lk:
                    es[v1] = True
                    es[v2] = True
                with lk:
                    rs[r] = True


def extract():
    lk = Lock()
    tr, vd, ts, mk_vd, mk_ts, es, rs = {}, {}, {}, {}, {}, {}, {}

    trd_cnt = int(os.getenv('TRD_CNT', '8'))
    tps = os.getenv('TPS', 'U_SE_C_I').split(',')

    tr_tm = int(datetime.strptime(os.getenv('TR_TM', ''), '%Y-%m-%d-%H').timestamp())
    vd_tm = int(datetime.strptime(os.getenv('VD_TM', ''), '%Y-%m-%d-%H').timestamp())
    ts_dm = int(datetime.strptime(os.getenv('TS_TM', ''), '%Y-%m-%d-%H').timestamp())
    st_dm = int(datetime.strptime(os.getenv('ST_TM', ''), '%Y-%m-%d-%H').timestamp())

    _ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_extract,
                   args=(tr, vd, ts, mk_vd, mk_ts, es, rs, tr_tm, vd_tm, ts_dm, st_dm, tps, lk, trd_cnt, i))
        t.start()
        _ts.append(t)
    for t in _ts:
        t.join()
    return tr, vd, ts, es.keys(), rs.keys()


def index(s, fn, pth):
    idx = {x: i for i, x in enumerate(s)}
    with open(f'{pth}/{fn}2id.txt', 'a') as f:
        f.write(f'{len(idx)}\n')
    with open(f'{pth}/{fn}2id.txt', 'a') as f:
        for x, i in idx.items():
            f.write(f'{x}\t{i}\n')
    return idx


def _write(d, pth, fn, e_idx, r_idx, lk, trd_cnt, prt):
    with open(f'{pth}/{fn}2id.txt', 'a') as fw:
        with open(f'{pth}/{fn}.txt', 'a') as fg:
            for i, x in enumerate(d):
                if i % trd_cnt != prt:
                    continue
                with lk:
                    fw.write(f'{e_idx[x[0]]}\t{e_idx[x[1]]}\t{r_idx[x[2]]}\t{x[3]}\n')
                with lk:
                    fg.write(f'{e_idx[x[0]]}\t{r_idx[x[2]]}\t{e_idx[x[1]]}\t{x[3]}\n')  # NOTE: GraphVite format


def _build(tr, vd, ts, pth, e_idx, r_idx, lk, trd_cnt, prt):
    _write(tr, pth, 'train', e_idx, r_idx, lk, trd_cnt, prt)
    _write(vd, pth, 'valid', e_idx, r_idx, lk, trd_cnt, prt)
    _write(ts, pth, 'test', e_idx, r_idx, lk, trd_cnt, prt)


def build(tr, vd, ts, pth, e_idx, r_idx):
    with open(f'{pth}/train2id.txt', 'a') as fw:
        fw.write(f'{len(tr)}\n')
    with open(f'{pth}/valid2id.txt', 'a') as fw:
        fw.write(f'{len(vd)}\n')
    with open(f'{pth}/test2id.txt', 'a') as fw:
        fw.write(f'{len(ts)}\n')

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
    pth = './data/split/temporal'
    if not os.path.isdir(pth):
        os.mkdir(pth)

    tr, vd, ts, es, rs = extract()
    e_idx = index(es, 'entity', pth)
    r_idx = index(rs, 'relation', pth)
    build(tr, vd, ts, pth, e_idx, r_idx)


if __name__ == '__main__':
    main()
