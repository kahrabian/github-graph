from queue import PriorityQueue,Queue
import re
from datetime import datetime
import random
import pickle

# TODO: string mapping to integer
# TODO: parallism in running repo_tree

def reg(s):
    r = re.match("\/(.*?)\/", s).groups()[0]
    return r

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
    :param dict1: dictionary of all repos
    :param:height: desired height of tree in exploration
    :param: ds: desired number of exploration
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
    :param dict1: dictionary of repo and its popscore, or the set of manually selection
    :param dict2: dictionary of entity and its repo as root
    :param n: the required number of sampling
    :param k: the initial set size
    :param m: the expanding size
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