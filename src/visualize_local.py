import glob
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import os
import queue
import random
import re

from datetime import datetime
from queue import PriorityQueue
from threading import Lock, Thread


def _extract(g, md, lk, trd_cnt, prt):
    st_tm = datetime.strptime(os.getenv('ST_TM', ''), '%Y-%m-%d-%H')
    sp_tm = datetime.strptime(os.getenv('SP_TM', ''), '%Y-%m-%d-%H')
    sd = 'graph' if md == 'G' else 'sample'
    for fn in glob.glob(f'./data/{sd}/*.txt'):
        fn_tm = datetime.strptime(fn, f'./data/{sd}/%Y-%m-%d-%H.txt')
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
    md = os.getenv('MD', 'G')
    for i in range(0, trd_cnt):
        t = Thread(target=_extract, args=(g, md, lk, trd_cnt, i))
        t.start()
        t.join()
    return g


def _transform(tg, g, gk, lk, trd_cnt, prt):
    for i, v in enumerate(gk):
        if i % trd_cnt != prt:
            continue
        tp_rx = re.compile(r'/(.*)/.*')
        tp = re.findall(tp_rx, v)[0]
        nv = len(g[v])
        with lk:
            if tp not in tg:
                tg[tp] = set()
            tg[tp].add((nv, v))


def transform(g):
    tg = {}
    lk = Lock()
    gk = sorted(g.keys())
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    for i in range(0, trd_cnt):
        t = Thread(target=_transform, args=(tg, g, gk, lk, trd_cnt, i))
        t.start()
        t.join()
    return tg


def _bfs(viz_g, g, viz_pl, viz_d, trd_cnt, prt):
    for i, (dx, x) in enumerate(viz_pl):
        if i % trd_cnt != prt:
            continue
        tp_rx = re.compile(r'/(.*)/(.*)')
        tp, pk = re.findall(tp_rx, x)[0]

        vs = set()
        mk = set()
        q = queue.Queue()
        mk.add(x)
        q.put((x, 0))
        while not q.empty():
            v, d = q.get()
            if d > viz_d:
                continue
            vs.add(v)
            for n in g[v] - mk:
                mk.add(n)
                q.put((n, d + 1))

        k = f'{dx}_{tp}_{pk}'
        for v in vs:
            if k not in viz_g:
                viz_g[k] = set()
            for u in (vs & g[v]):
                # NOTE: To reduce memory footprint
                viz_g[k].add((max(v, u), min(v, u)))


def bfs(g, tg):
    viz_cnt = int(os.getenv('VIZ_CNT', '10'))
    viz_pl = []
    for k, v in tg.items():
        viz_pl += sorted(v, reverse=True)[:viz_cnt]

    viz_g = {}
    lk = Lock()
    viz_d = int(os.getenv('VIZ_D', '3'))
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    for i in range(0, trd_cnt):
        t = Thread(target=_bfs, args=(viz_g, g, viz_pl, viz_d, trd_cnt, i))
        t.start()
        t.join()
    return viz_g


def _build(plt_g, viz_g, viz_gk, cm, lk, trd_cnt, prt):
    for i, k in enumerate(viz_gk):
        if i % trd_cnt != prt:
            continue
        vs = []
        tp_rx = re.compile(r'/(.*)/.*')
        for v in set(itertools.chain.from_iterable(viz_g[k])):
            tp = re.findall(tp_rx, v)[0]
            vs.append((v, {'color': cm[tp]}))

        net = nx.Graph()
        net.add_nodes_from(vs)
        net.add_edges_from(viz_g[k])

        plt_g.append((net, k))


def build(viz_g):
    from configs.graph import schema as cfg_schema

    cm = {}
    cp = ['#111d5e', '#46b5d1', '#b21f66', '#f65c78', '#2d334a', '#c3f584', '#ff7315', '#ffd271', '#fff3af']
    for i, tp in enumerate(sorted(cfg_schema.schema.keys())):
        cm[tp] = cp[i]

    plt_g = []
    lk = Lock()
    viz_gk = sorted(viz_g.keys())
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(plt_g, viz_g, viz_gk, cm, lk, trd_cnt, i))
        t.start()
        t.join()
    return plt_g


def plot(plt_g):
    for net, k in plt_g:
        tp_rx = re.compile(r'([^_]*)_(.*)_([^_]*)')
        d, tp, pk = re.findall(tp_rx, k)[0]

        dir_pth = f'./results/visualizations/local/{tp}'
        if not os.path.isdir(dir_pth):
            os.mkdir(dir_pth)

        fig = plt.figure(figsize=(100, 100))
        ax = fig.add_subplot(111)

        nc = [net.nodes[v]['color'] for v in net]
        pos = nx.fruchterman_reingold_layout(net)
        nx.draw_networkx(net, pos, node_color=nc)

        plt.tight_layout()
        plt.savefig(f'{dir_pth}/{pk}_{d}.png', format='PNG')


def main():
    g = extract()
    tg = transform(g)
    viz_g = bfs(g, tg)
    plt_g = build(viz_g)
    plot(plt_g)


if __name__ == '__main__':
    main()
    exit(0)
