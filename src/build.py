import glob
import json
import os
from datetime import datetime
from threading import Thread

from configs.graph import issue_comment as cfg_issue_comment
from configs.graph import issues as cfg_issues
from configs.graph import member as cfg_member
from configs.graph import pull_request_review_comment as cfg_pull_request_review_comment
from configs.graph import pull_request as cfg_pull_request
from configs.graph import push as cfg_push
from configs.graph import schema as cfg_schema
from configs.graph import watch as cfg_watch


def get_config():
    config = {}
    config.update(cfg_issue_comment.config)
    config.update(cfg_issues.config)
    config.update(cfg_member.config)
    config.update(cfg_pull_request_review_comment.config)
    config.update(cfg_pull_request.config)
    config.update(cfg_push.config)
    config.update(cfg_watch.config)

    return config


def get_schema():
    return cfg_schema.schema


def fetch(key, data):
    steps = key.split('.')
    data = data.copy()
    try:
        for step in steps:
            data = data[step]
    except KeyError:
        return ''
    return data


def build(year, total, part):
    gconfig = get_config()
    gschema = get_schema()
    for fn in glob.glob(f'/scratch/kahrab/github-graph/data/events/{year}/*.json'):
        fn_time = datetime.strptime(fn, f'/scratch/kahrab/github-graph/data/events/{year}/%Y-%m-%d-%H.json')
        inc_path = fn_time.strftime(f'./data/graph/{year}/_%Y-%m-%d-%H.txt')
        com_path = fn_time.strftime(f'./data/graph/{year}/%Y-%m-%d-%H.txt')
        if fn_time.timetuple().tm_yday % total != part or os.path.exists(com_path):
            continue
        with open(fn, 'r') as fr:
            with open(inc_path, 'w') as fw:
                for l in fr.readlines():
                    r = l.strip()
                    if r == '':
                        continue
                    event = json.loads(r)
                    event_type = event['type']
                    if event_type in gconfig:
                        for entity in gconfig[event_type]['entities']:
                            if 'type_field' not in entity['e'] or \
                                    fetch(entity['e']['type_field'], event) in entity['e']['type'].keys():
                                v1 = {}
                                for feature in gschema[entity['v1']['type']]['features']:
                                    key = entity['v1']['features'][feature]
                                    v1[feature] = fetch(key, event)

                                e = {}
                                if type(entity['e']['type']) == dict:
                                    key = fetch(entity['e']['type_field'], event)
                                    e['type'] = entity['e']['type'][key]
                                else:
                                    e['type'] = entity['e']['type']
                                for feature in entity['e']['features']:
                                    e[feature] = fetch(feature, event)

                                v2 = {}
                                for feature in gschema[entity['v2']['type']]['features']:
                                    key = entity['v2']['features'][feature]
                                    v2[feature] = fetch(key, event)

                                fw.write(f"/{entity['v1']['type']}/{v1['id']}\t")
                                fw.write(f"/{entity['v2']['type']}/{v2['id']}\t")
                                fw.write(f"{e['type']}\t")
                                if len(e) == 1:
                                    fw.write(f"{e['created_at']}\n")
                                else:
                                    fw.write(f"{e['created_at']}\t")
                                    for k, v in e.items():
                                        if k in ['created_at', 'type']:
                                            continue
                                        fw.write(f"{k.split('.')[-1]}:{v}\t")
                                    fw.write('\n')
            os.rename(inc_path, com_path)


def main():
    year = int(os.getenv('YEAR', '2019'))
    total_threads = int(os.getenv('TOTAL_THREADS', '36'))
    task_id = int(os.getenv('SLURM_ARRAY_TASK_ID', '-1'))
    ts = []
    for i in range(task_id * 2, (task_id + 1) * 2):
        t = Thread(target=build, args=(year, total_threads, i))
        t.start()
        ts.append(t)
    for t in ts:
        t.join()


if __name__ == '__main__':
    main()
