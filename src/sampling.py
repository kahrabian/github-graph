from queue import PriorityQueue,Queue
import re
from datetime import datetime
import random
import pickle

def reg(s):
    r = re.match("\/(.*?)\/", s).groups()[0]
    return r

def time_dict_build(gt):
    """
    This method use to build up the earliest and the latest timestamp for the entity
    :param gt: the dict of graph key:value~(node,timestamp): adjecentN(node)
    :return: dt_e,dt_l the dictionary for the timestamp
    """
    dt_e ={}
    dt_l = {}
    for v,t in gt.keys():
        if v not in dt_e:
            dt_e[v] = t
        if v not in dt_l:
            dt_l[v] = t
        dt_e[v] = min(datetime.strptime(dt_e[v], '%Y-%m-%d'),datetime.strptime(t, '%Y-%m-%d')).strftime('%Y-%m-%d')
        dt_l[v] = max(datetime.strptime(dt_l[v], '%Y-%m-%d'),datetime.strptime(t, '%Y-%m-%d')).strftime('%Y-%m-%d')
    return dt_e,dt_l

def pop_score(g, dt_e, dt_l, w_p, w_t):
    """
    The functions use BFS to traverse the tree component with repo as root. The pop_score will be
    composed of the sum of children
    :param g: the dict of graph key:value~node: adjecentN(node)
    :param dt_e: dictionary of entity and its earliest timestamp
    :param dt_l: dictionary of entity and its latest timestamp
    :param w_p: the weight on popularity score
    :param w_t: the weight on the long time span focus
    :return: dict1: key:value~(repo): initial_pop_score
    """
    d = {}  # NOTE: Already seen nodes

    for key, value in g.items():
        if key not in d and reg(key) == "repo":
            # running BFS algorithm
            mk = {}
            q = Queue()
            q.put(key)

            cmp_size = 0
            earliest_time = datetime.strptime(dt_e[key], '%Y-%m-%d')
            latest_time = None

            while not q.empty():
                v = q.get()
                mk[v] = True
                cmp_size += 1
                current_time = datetime.strptime(dt_l[v], '%Y-%m-%d')
                if latest_time is None or latest_time < current_time:
                    latest_time = current_time
                for u in g[v]:  # - set(mk.keys())
                    if not mk.get(u, False) and reg(u) != 'user' and reg(u) != 'repo':
                        q.put(u)
                    elif reg(u) == 'user':
                        # count the user but other than that do nothing
                        cmp_size += 1
            cmp_size = cmp_size * w_p + w_t * abs(latest_time - earliest_time).days
            d[key] = cmp_size
    return d

def root_repo_tree(g, dict1, isolate=True):
    """
    Implmented the BFS algorithms to build up repo tree in the forest
    :param g:  the dict of graph key:value~(node,timestamp): adjecentN(node)
    :param dict1: dictionary of all repos
    :return: dict2 for pop_samping: key:value~(node): list of repo it connected to
    """
    p = {}
    print("Length", len(dict1))
    for key, value in dict1.items():
        mk = set()
        Q = Queue()
        Q.put((key, 0))

        while not Q.empty():
            v, l = Q.get()
            # print("v:", v)
            mk.add(v)
            if v not in p:
                p[v] = []
                # print("V",v," ",l," ",len(mk))
            p[v].append(key)

            # remove
            # if not isolate and (l > height or len(mk) > ds):
            #     break

            if isolate and (reg(v) == 'user' or (reg(v) == 'repo' and v != key)):
                continue
            else:
                for u in g[v] - mk:
                    Q.put((u, l + 1))
                # print("U", u)

    return p

def weighted_random_by_dct(dct):
    rand_val = random.random()
    total = 0
    for k, v in dct.items():
        total += v
        if rand_val <= total:
            return k, v
    assert False, 'unreachable'

def adjust_score(dict1, node, n_common_user, w_a):
    """
    :param dict1: dict of repo: pop_socre
    :param node: repo node
    :param n_common_user: the number of count of common users
    :param w_a: weight
    :return: adjust score
    """

    s = dict1[node]
    adj_s = s + (n_common_user - 1) * s / w_a

    return adj_s

def pop_sampling_v2(g, dict1, dict2, n, k, m, w_a, p, ini_op=1):
    """
    :param g: the dict of graph key:value~(node,timestamp): adjecentN(node)
    :param dict1: dictionary of repo and its popscore, or the set of manually selection
    :param dict2: dictionary of entity and its repo as root
    :param n: the required number of sampling
    :param k: the initial set size
    :param m: the expanding size
    :param w_a: the reweight for popsocre
    :param p: the pre-set probability threshold
    :parameter ini_op: 1 top repos based on pop_score, 2 manual selection - just change the input dict1, 3 random sample based on pop_score
    :return: a set of sampled entity
    """
    U = set()  # NOTE: Selected nodes
    Q = PriorityQueue()  # NOTE: Repos
    print(len(g.keys()))
    ### initial sampling
    # 1 top repos based on pop_score
    # 2 manual selection - just change the input dict1
    # 3 random sample based on pop_score
    if ini_op == 1:
        # sorted(dict1.items(), key=lambda x: x[1], reverse=True)[:k]
        for s, v in sorted(map(lambda x: (x[1], x[0]), dict1.items()), reverse=True)[:k]:
            Q.put((-s, v))
    elif ini_op == 2:
        # U = set(dict1.keys())
        # with the assumption that the size already k
        for v, s in dict1.items():
            Q.put((-s, v))
    elif ini_op == 3:
        while Q.qsize() < k:
            # u, v = weighted_random_by_dct(dict1)
            v, s = weighted_random_by_dct(dict1)
            # U.add(u)
            Q.put((-s, v))
    else:
        raise ValueError("Invalid initial option")

    print("Initial_Size:", Q.qsize())

    vs = set()  # NOTE: Set of already seen nodes
    us = set()  # NOTE: Set of already seen Users
    while not Q.empty() and len(vs) < n:
        s, root = Q.get()
        U.add(root)
        vs.add(root)

        gc = {}
        Q_v = Queue() # NOTE: BFS queue
        Q_v.put(root)
        # print(len(vs))
        while not Q_v.empty() and len(vs) < n:  # NOTE: If we are in middle of component we could ignore the size restriction
            v = Q_v.get()
            # BFS
            for u in g[v] - vs:  # NOTE: You don't need this, you can iterate over all of them
                if reg(u) == 'user':
                    for r in dict2[u]:
                        if r not in gc and r != root:
                            gc[r] = 0
                        if r!=root:
                            gc[r] += 1
                    us.add(u)
                    # us[u] = max(-s, us.get(u, 0))
                else:
                    vs.add(u)
                    Q_v.put(u)

        for v, w in gc.items():
            gc[v] = adjust_score(dict1,  v, w, w_a)

        if random.uniform(0, 1) < p and len(vs) < n:
            for r,s in sorted(gc.items(), key=lambda x: x[1], reverse=True)[:min(len(gc), m)]:
                if r not in vs:
                    Q.put((-dict1[r], r))
        if Q.empty() and len(vs) < n:
            nb = set(dict1.keys()) - U
            for s, v in sorted([(dict1[r], r) for r in nb], key=lambda x: x[0], reverse=True)[:k]:
                Q.put((-s, v))
    vs = vs.union(us)
    print("Finish sampling", len(vs))
    return vs

def read_dict(dict_name,path='./data/'):
    dct = pickle.load(open(path+ dict_name+'.txt', 'rb'))
    return dct

def write_dict(dict_name,dct,path='./data/'):
    # as requested in comment
    pickle.dump(dct, open(path+ dict_name+'.txt', 'wb'))
