import glob
import json
import os
from datetime import datetime
from threading import Lock, Thread


def build(_id, lk, total, part):
    for fn in glob.glob(f'/scratch/kahrab/github-graph/data/events/*/*.json'):
        fn_time = datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.json')
        if fn_time.timetuple().tm_yday % total != part:
            continue
        with open(fn, 'r') as fr:
            for l in fr.readlines():
                r = l.strip()
                if r == '':
                    continue
                event = json.loads(r)
                if 'repo' in event:
                    with lk:
                        _id[f'/repo/{event["repo"]["id"]}'] = event['repo']['name']


def main():
    total_threads = int(os.getenv('TOTAL_THREADS', '36'))
    task_id = int(os.getenv('SLURM_ARRAY_TASK_ID', '-1'))
    lk = Lock()
    ts = []
    _id = {}
    for i in range(task_id * 2, (task_id + 1) * 2):
        t = Thread(target=build, args=(_id, lk, total_threads, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()
    with open(f'./data/tmp/id_{task_id}.json', 'w') as f:
        f.write(json.dumps(_id))


if __name__ == '__main__':
    main()
