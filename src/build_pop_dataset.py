import glob
import random
import os
import re
from datetime import datetime
import pandas as pd
from queue import PriorityQueue
from threading import Lock, Thread

def reg(s):
    r = re.match("\/(.*?)\/", s).groups()[0]
    return r

def _extract(g, lk, trd_cnt, prt):
    st_tm = datetime.strptime('2019-12-25-00', '%Y-%m-%d-%H')
    sp_tm = datetime.strptime('2019-12-27-23', '%Y-%m-%d-%H')
    for fn in glob.glob('./data/graph/*.txt'):
        fn_tm = datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                #head, tail, relation, time
                v1, r ,v2, t = l.strip().split('\t')
                date1 = datetime.strptime(t[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                tuple1 = (v1,date1)
                tuple2 = (v2,date1)

                with lk:
                    if tuple1 not in g:
                        g[tuple1] = set()
                    g[tuple1].add(tuple2)

                with lk:  # NOTE: To find nodes with the most interactions
                    if tuple2 not in g:
                        g[tuple2] = set()
                    g[tuple2].add(tuple1)

def extract():
    g = {}
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_extract, args=(g, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    # print(g)
    return g

def sample(g):
    # in_sz = int(os.getenv('IN_SZ', '100'))
    # tg_sz = int(os.getenv('TG_SZ', '10000'))
    # smpl_rt = int(os.getenv('SMPL_RT', '100'))
    in_sz = 100
    tg_sz = 10000
    smpl_rt = 100

    mk = set()
    q = PriorityQueue()

    # intial set
    for _, v in sorted(map(lambda x: (len(x[1]), x[0]), g.items()), reverse=True)[:in_sz]:
        #maybe check the entity of the v here, according the entity of v
        # check g[v] and put a changed length
        # focuse on the repo
        if(reg(v[0])=="repo"):
            # popular user have a lot of activity
            # U_HS_A_R, U_HS_R_R user start the repo might have low weighted
            temp = 0
            for x in g[v]:
                if reg(x[0]) == "user" or reg(x[0]) == "repo":
                    temp += 1
                else:
                    # issue left
                    temp += 0.5
                temp *= 365
                # temp *= 60
                # date1 = datetime.strptime(v[1], '%Y-%m-%d')
                # date2 = datetime.strptime(x[1], '%Y-%m-%d')
                # days = (date1-date2).days  # Build-in datetime function
                # days = divmod(days, 86400)[0]
                # print(days)
                # temp += days
            q.put(((-temp), v))
            mk.add(v)
        else:
            continue
    # print(mk)
    print("Size",q.qsize())
    vs = set()
    while not q.empty() and len(vs) < tg_sz:

        _, v1 = q.get()
        # print(v)
        vs.add(v1[0])
        date1 = datetime.strptime(v1[1], '%Y-%m-%d')

        ss = g.get(v1, set()) - mk
        for n in random.sample(ss, min(len(ss), smpl_rt)):
            mk.add(n)
            q.put((-len(g.get(n, [])), n))
        if q.empty():
            ss = set(g.keys()) - mk
            for _, v in sorted(map(lambda x: (len(x), x), ss), reverse=True)[:min(in_sz, tg_sz - len(vs))]:

                if (reg(v[0]) == "user"):
                    # popular user have a lot of activity
                    # U_HS_A_R, U_HS_R_R user start the repo might have low weighted
                    diff = 0
                    for x in g[v]:
                        date2 = datetime.strptime(x[1], '%Y-%m-%d')
                        days = abs((date1 - date2).days)  # Build-in datetime function
                        if days > diff:
                            diff = days
                    q.put((-(len(g[v])*60+diff), v))
                elif (reg(v[0]) == "pr"):
                    # pr_review，pr_review_comment
                    temp = 0
                    diff = 0
                    for x in g[v]:
                        if reg(x[0]) == "pr_review" or reg(x[0]) == "pr_review_comment":
                            temp += 1
                        date2 = datetime.strptime(x[1], '%Y-%m-%d')
                        days = abs((date1 - date2).days)  # Build-in datetime function
                        if days > diff:
                            diff = days
                    q.put((-(temp*60 + diff), v))

                elif (reg(v[0]) == "issue"):
                    # issue_comment
                    temp = 0
                    diff = 0
                    for x in g[v]:
                        if reg(x[0]) == "issue_comment":
                            temp += 1
                        date2 = datetime.strptime(x[1], '%Y-%m-%d')
                        days = abs((date1 - date2).days)  # Build-in datetime function
                        if days > diff:
                            diff = days
                    q.put((-(temp*60 + diff), v))

                elif (reg(v[0]) == "repo"):
                    # repo is popular
                    temp = 0
                    diff = 0
                    for x in g[v]:
                        if reg(x[0]) == "user" or reg(x[0]) == "repo":
                            temp += 1
                        else:
                            # issue left
                            temp += 0.5
                        date2 = datetime.strptime(x[1], '%Y-%m-%d')
                        days = abs((date1 - date2).days)  # Build-in datetime function
                        if days > diff:
                            diff = days
                    q.put((-(temp*60 + diff), v))
                else:
                    # not consider as popular
                    diff =0
                    for x in g[v]:
                        date2 = datetime.strptime(x[1], '%Y-%m-%d')
                        days = abs((date1 - date2).days)  # Build-in datetime function
                        if days > diff:
                            diff = days
                    q.put((-(len(g[v])*60+diff), v))
                mk.add(v)
    return vs

def dfs(visited, graph, node):
    if node not in visited:
        print (node)
        visited.add(node)
        for neighbour in graph[node]:
            dfs(visited, graph, neighbour)

def _build(vs, trd_cnt, prt):
    st_tm = datetime.strptime('2019-12-25-00', '%Y-%m-%d-%H')
    sp_tm = datetime.strptime('2019-12-27-23', '%Y-%m-%d-%H')
    for fn in glob.glob('./data/graph/*.txt'):
        fn_tm = datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt')
        inc_pth = fn_tm.strftime('./data/sample/pop_%Y-%m-%d-%H.txt')
        com_pth = fn_tm.strftime('./data/sample/pop_%Y-%m-%d-%H.txt')
        # if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.timetuple().tm_yday % trd_cnt != prt or os.path.exists(com_pth):
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
        # print(fn)
        with open(fn, 'r') as fr:
            # print(fr)
            with open(inc_pth, 'w') as fw:
                for l in fr.readlines():
                    v1, r, v2, _ = l.split('\t')
                    # print(v1,v2)
                    if v1 in vs and v2 in vs:
                        # print("write")
                        fw.write(l)
        os.rename(inc_pth, com_pth)

def build(vs):
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_build, args=(vs, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()

def _extract_graph(g, lk, trd_cnt, prt):
    st_tm = datetime.strptime('2019-12-25-00', '%Y-%m-%d-%H')
    sp_tm = datetime.strptime('2019-12-27-23', '%Y-%m-%d-%H')
    for fn in glob.glob('./data/sample/*.txt'):
        fn_tm = datetime.strptime(fn, './data/sample/pop_%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
    # fn = './data/test.txt'
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                #head, tail, relation, time
                v1, r ,v2, t = l.strip().split('\t')
                date1 = datetime.strptime(t[:10], '%Y-%m-%d').strftime('%Y-%m-%d')
                tuple1 = (v1, date1)
                tuple2 = (v2, date1)

                with lk:
                    if v1 not in g:
                        g[v1] = []
                    g[v1].append(tuple2)

                with lk:  # NOTE: To find nodes with the most interactions
                    if v2 not in g:
                        g[v2] = []
                    g[v2].append(tuple1)

def extract_graph():
    g = {}
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_extract_graph, args=(g, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    # print(g)
    # _extract_graph(g, lk, trd_cnt,0)
    # print(g)
    return g

def longest_path():
    g = extract_graph()
    d = {}
    d2 ={}
    node = 0
    edge = 0
    max_d = 0
    min_d = 1
    # print(g)
    for v,value in g.items():
        maxdate = value[0][1]
        mindate = value[0][1]
        for x in value:
            # print(t,x[1])
            if(x[1]>maxdate):
                maxdate = x[1]
            if(x[1]<mindate):
                mindate = x[1]
        days = abs((datetime.strptime(maxdate, '%Y-%m-%d') - datetime.strptime(mindate, '%Y-%m-%d')).days)
        d2[v] = days
        node += 1
        edge_c = len(value)
        edge += edge_c
        if edge_c not in d:
            d[edge_c] = 0
        d[edge_c] = d[edge_c] + 1
        max_d = max(max_d, edge_c)
        min_d = min(min_d, edge_c)
    edge /= 2
    avg_d = edge / node
    mid = 0
    mid1 = -1
    if node % 2 == 0:
        temp1 = node / 2
        temp2 = (node / 2) + 1
        #     even number
        for key, value in sorted(d.items()):
            temp1 -= value
            temp2 -= value
            if temp1 <= 0 and mid1 < 0:
                mid1 = key
            if temp2 <= 0:
                mid = (mid1 + key) / 2
                break
    else:
        temp = (node - 1) / 2
        #     odd number (node-1)/2
        for key, value in d.items():
            temp -= value
            if temp <= 0:
                mid = key
                break
    max_value = max(d2.values())
    # print(d2)
    print('Node:{}, Edge:{}, Max_d:{}, Min_d:{}, Avg_d:{}, Mid_d:{}, Lt: {}'.format(node, edge, max_d, min_d, avg_d, mid,max_value))


def main():
    g = extract()
    vs = sample(g)
    build(vs)


if __name__ == '__main__':
    random.seed(2020)
    # main()
    # with open('./data/test.txt', 'w') as f:
    #     for key, value in extract_graph().items():
    #         f.write('{} {} '.format(key,value))
    longest_path()
    # a = '2020-12-25'
    # b = '2020-12-27'
    # time1 = datetime.strptime(a, '%Y-%m-%d')  # convert string to time
    # time2 = datetime.strptime(b, '%Y-%m-%d')
    # days = time1 - time2
    # print(abs(days.days))


