import glob
import json
import os
from datetime import datetime
from threading import Thread


def build(total, part):
    for fn in glob.glob('/scratch/kahrab/github-graph/data/events/*/*.json'):
        fn_time = datetime.strptime(fn.split('/')[-1], '%Y-%m-%d-%H.json')
        inc_path = fn_time.strftime('./data/pr/_%Y-%m-%d-%H.txt')
        com_path = fn_time.strftime('./data/pr/%Y-%m-%d-%H.txt')
        if fn_time.timetuple().tm_yday % total != part or os.path.exists(com_path):
            continue
        with open(fn, 'r') as fr:
            with open(inc_path, 'w') as fw:
                for l in fr.readlines():
                    r = l.strip()
                    if r == '':
                        continue
                    event = json.loads(r)
                    if event['type'] == 'PullRequestEvent':
                        pr = event['payload']['pull_request']['id']
                        url = event['payload']['pull_request']['url']
                        fw.write(f"/pr/{pr}\t{url}\n")
            os.rename(inc_path, com_path)


def main():
    total_threads = int(os.getenv('TOTAL_THREADS', '36'))
    task_id = int(os.getenv('SLURM_ARRAY_TASK_ID', '-1'))
    ts = []
    for i in range(task_id * 2, (task_id + 1) * 2):
        t = Thread(target=build, args=(total_threads, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


if __name__ == '__main__':
    main()
