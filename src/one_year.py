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

    g_p = './data/g.pkl'
    if os.path.exists(g_p):
        g = load(g_p)
    else:
        g = graph(trd_cnt)
        dump(g_p, g)
    print(f'graph size: {len(g)}')

    roots = {
        # 'microsoft/vscode': '/repo/41881900',
        'rails/rails': '/repo/8514',
        'dimagi/commcare-hq': '/repo/247278',
        'tgstation/tgstation': '/repo/3234987',
        'symfony/symfony': '/repo/458058',
        'owncloud/core': '/repo/5550552',
        'Baystation12/Baystation12': '/repo/2715933',
        'joomla/joomla-cms': '/repo/2464908',
        'Wikia/app': '/repo/5532313',
        'rapid7/metasploit-framework': '/repo/2293158',
        'twbs/bootstrap': '/repo/2126244',
        'dlang/dmd': '/repo/1257070',
        'cdnjs/cdnjs': '/repo/1409811',
        'puppetlabs/puppet': '/repo/910744',
        'adobe/brackets': '/repo/2935735',
        'sympy/sympy': '/repo/640534',
        'wet-boew/wet-boew': '/repo/4297273',
        'Katello/katello': '/repo/4007018',
        'cocos2d/cocos2d-x': '/repo/1093228',
        'zendframework/zendframework': '/repo/702550',
        'angular/angular.js': '/repo/460078',
        'cakephp/cakephp': '/repo/656494',
        'scala/scala': '/repo/2888818',
        'ipython/ipython': '/repo/658518',
        'nodejs/node-v0.x-archive': '/repo/211666'
    }
    for fn, root in roots.items():
        p = fn.replace("/", "_")
        vs_p = f'./data/vs_{p}.pkl'
        if os.path.exists(vs_p):
            vs = load(vs_p)
        else:
            vs = bfs(g, root)
            dump(vs_p, vs)
        print(f'sample node size {fn}: {len(vs)}')

        build(vs, p, trd_cnt)
