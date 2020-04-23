import glob
import random
import os
import re
from datetime import datetime
import pandas as pd
import pickle
from queue import PriorityQueue,Queue
from threading import Lock, Thread

def reg(s):
    r = re.match("\/(.*?)\/", s).groups()[0]
    return r

def _t_extract(g, lk, trd_cnt, prt):
    st_tm = datetime.strptime('2019-12-25-00', '%Y-%m-%d-%H')
    sp_tm = datetime.strptime('2019-12-25-20', '%Y-%m-%d-%H')
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

def t_extract():
    g = {}
    lk = Lock()
    trd_cnt = int(os.getenv('TRD_CNT', '16'))
    ts = []
    for i in range(0, trd_cnt):
        t = Thread(target=_t_extract, args=(g, lk, trd_cnt, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    # print(g)
    return g

def _extract(g, lk, trd_cnt, prt):
    st_tm = datetime.strptime('2019-12-25-00', '%Y-%m-%d-%H')
    sp_tm = datetime.strptime('2019-12-25-20', '%Y-%m-%d-%H')
    for fn in glob.glob('./data/graph/*.txt'):
        fn_tm = datetime.strptime(fn, './data/graph/%Y-%m-%d-%H.txt')
        if fn_tm < st_tm or fn_tm > sp_tm or fn_tm.timetuple().tm_yday % trd_cnt != prt:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                #head, tail, relation, time
                v1, r ,v2, t = l.strip().split('\t')

                with lk:
                    if v1 not in g:
                        g[v1] = set()
                    g[v1].add(v2)

                with lk:  # NOTE: To find nodes with the most interactions
                    if v2 not in g:
                        g[v2] = set()
                    g[v2].add(v1)

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
                    continue
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


    print("Size",len(vs))
    return vs

def pop_score(g, w_p, w_t):
    """
    :param g: the dict of graph key:value~(node,timestamp): adjecentN(node)
    :param w_p: the weight on popularity score
    :param w_t: the weight on the long time span focus
    :return: dict1: key:value~(repo): initial_pop_score
    """
    d = {}
    for key, value in g.items():
        if key[0] not in d:
            if reg(key[0]) == "repo":
                # popular user have a lot of activity
                # U_HS_A_R, U_HS_R_R user start the repo might have low weighted
                temp = 0
                date1 = datetime.strptime(key[1], '%Y-%m-%d')
                diff = 0
                for x in value:
                    if reg(x[0]) == "user" or reg(x[0]) == "repo":
                        temp += 1
                    else:
                        temp += 0.5
                    temp *= w_p
                    date2 = datetime.strptime(x[1], '%Y-%m-%d')
                    days = abs((date1 - date2).days)
                    if days > diff:
                        diff = days
                    temp += diff * w_t
                d[key[0]] = temp
    return d

def root_repo_tree(g, dict1,height,ds,option=1):
    """
    Implmented the kruskal's algorithms to build up repo tree in the forest
    :param g:  the dict of graph key:value~(node,timestamp): adjecentN(node)
    :return: dict2 for pop_samping: key:value~(node): set of repo it connected to
    """
    # traversal upto the user

    d = {}
    Q = Queue()
    print("Length",len(dict1))
    for key, value in dict1.items():
        # BFS
        seen = set()
        Q.put((key,0))
        # print(key)
        while not Q.empty():
            v = Q.get()
            # print(v)
            if v[0] not in d:
                d[v[0]] = set()
            seen.add(v[0])
            d[v[0]].add(key)

            if v[1] >height or len(seen) > ds:
                break

            if option ==1:
                if reg(v[0]) == 'user':
                    continue
                else:
                    for n in g.get(v[0], [])-seen:
                        Q.put((n,v[1]+1))
            else:

                for n in g.get(v[0], [])-seen:
                    Q.put((n,v[1]+1))
        seen.clear()
    return d
# mapping string into


def weighted_random_by_dct(dct):
    rand_val = random.random()
    total = 0
    for k, v in dct.items():
        total += v
        if rand_val <= total:
            return k, v
    assert False, 'unreachable'


def only_user_left(Q):
    for x in Q.queue:
        v = x[1]
        if reg(v) != 'user':
            return False
    return True


def adjust_score(dict1, dict2, node, g, w):
    try:
        root_repo = dict2[node]
        s = dict1[root_repo]
        adj_nodes = g[s]
        n_user = 0
        for n in adj_nodes:
            if reg(n) == 'user':
                n_user += 1
        adj_s = s + (n_user - 1) * s / w
        return adj_s
    except:
        return 0


def pop_sampling_v2(g, dict1, dict2, n, k, m, w, p, ini_op=1):
    """
    :param g: the dict of graph key:value~(node,timestamp): adjecentN(node)
    :param n: the required number of sampling
    :param dict1: dictionary of repo and its popscore, or the set of manually selection
    :param dict2: dictionary of entity and its repo as root
    :param k: the initial set size
    :param m: the expanding size
    :param w_p: the weight on popularity score
    :param w_t: the weight on the long time span focus
    :param w: the reweight for popsocre
    :param p: the pre-set probability threshold
    :parameter ini_op: 1 top repos based on pop_score, 2 manual selection - just change the input dict1, 3 random sample based on pop_score
    :return: a set of sampled entity
    """

    U = set()
    Q = PriorityQueue()
    print(len(g.keys()))
    ### initial sampling
    # 1 top repos based on pop_score
    # 2 manual selection - just change the input dict1
    # 3 random sample based on pop_score
    try:
        if ini_op == 1:
            for s, v in sorted(map(lambda x: (x[1], x[0]), dict1.items()), reverse=True)[:k]:
                Q.put((-s, v))
                U.add(v)
        elif ini_op == 2:
            U = set(dict1.keys())
            # with the assumption that the size already k
            for u in U:
                Q.put((-dict1[u], u))
        elif ini_op == 3:
            while len(U) < k:
                u, v = weighted_random_by_dct(dict1)
                U.add(u)
                Q.put((-v, u))
        else:
            raise ValueError("Invalid initial option")
    except ValueError as ve:
        print(ve)

    print("Initial_Size:",len(U))
    ### growth
    vs = set()
    ul = {}
    while not Q.empty() and len(vs) < n:

        score, v1 = Q.get()
        vs.add(v1)
        print(len(vs))
        if reg(v1) == 'user':
            if v1 in ul:
                ul[v1] = max(-score, ul[v1])
            else:
                ul[v1] = -score
        else:
            # remove the one that have already seen
            nb = g.get(v1, set()) - U
            # BFS
            for nn in random.sample(nb, min(len(nb), m)):
                U.add(nn)
                try:
                    if reg(nn) == 'repo':
                        Q.put((-dict1[nn], nn))
                    else:
                        R = dict2.get(nn,[])
                        if len(R) > 1:
                            R_d = {r: dict1[r] for r in R}
                            Q.put((-max(R_d.values()), nn))
                        elif len(R) == 1:
                            r = R.pop()
                            Q.put((-dict1[r], nn))
                        else:
                            continue
                except ValueError:
                    continue
        # until all are leaf users
        if Q.empty() and len(ul) > 0:
            u = max(ul, key=ul.get)
            ul.pop(u)
            Y = dict2.get(u,[])
            nb = Y - U
            # check threshold
            if random.uniform(0, 1) < p and len(vs) < n:
                for nn in random.sample(nb, min(len(nb), m)):
                    # Z < - randomSample(m, adjustScores(Y))
                    # use Y to calculate the adjustScore for n
                    adj_s = adjust_score(dict1, dict2, nn, g, w)
                    if adj_s ==0:
                        R = dict2.get(nn, [])
                        if len(R) > 1:
                            R_d = {r: dict1[r] for r in R}
                            Q.put((-max(R_d.values()), nn))
                        elif len(R) == 1:
                            r = R.pop()
                            Q.put((-dict1[r], nn))
                    else:
                        Q.put((-adj_s, nn))
        # keep sure we can continue sampling
        elif Q.empty() and len(vs) < n:
            nb = set(g.keys()) - U
            for _, v in sorted(map(lambda x: (len(x), x), nb), reverse=True)[:min(k, n - len(vs))]:
                U.add(v)
                Q.put((-len(g.get(v, [])), v))
    print("Finish sampling", len(vs))
    return vs

def read_dict(dict_name,path='./data/'):
    dct = pickle.load(open(path+ dict_name+'.txt', 'rb'))
    return dct

def write_dict(dict_name,dct,path='./data/'):
    # as requested in comment
    pickle.dump(dct, open(path+ dict_name+'.txt', 'wb'))

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
    tg = t_extract()
    dict1 =  pop_score(tg,60,1)
    # write_dict('dict1',dict1)
    #dict1 = read_dict('dict1')
    #dict2 = read_dict('dict2')
    # print(dict1)
    g = extract()
    # # print(dict1)
    #print(g['/repo/188237225'])
    dict2 = root_repo_tree(g, dict1,100,4,option=1)
    # write_dict('dict2', dict2)
    print("Dict1 and Dict2 Finished")
    vs = pop_sampling_v2(g, dict1, dict2, 5000, 5, 100, 50, 0.5, ini_op=1)
    # # vs = sample(g)
    build(vs)
    longest_path()

if __name__ == '__main__':
    random.seed(2020)
    main()

    # with open('./data/test.txt', 'w') as f:
    #     for key, value in extract_graph().items():
    #         f.write('{} {} '.format(key,value))
    # longest_path()
    # a = '2020-12-25'
    # b = '2020-12-27'
    # time1 = datetime.strptime(a, '%Y-%m-%d')  # convert string to time
    # time2 = datetime.strptime(b, '%Y-%m-%d')
    # days = time1 - time2
    # print(abs(days.days))


