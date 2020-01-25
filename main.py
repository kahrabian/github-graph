import glob
import json
import os
import threading

from datetime import datetime


def get_config():
    from configs import commit_comment as cfg_commit_comment
    from configs import fork as cfg_fork
    from configs import issue_comment as cfg_issue_comment
    from configs import issues as cfg_issues
    from configs import member as cfg_member
    from configs import pull_request_review_comment as cfg_pull_request_review_comment
    from configs import pull_request_review as cfg_pull_request_review
    from configs import pull_request as cfg_pull_request
    from configs import push as cfg_push
    from configs import star as cfg_star

    config = {}
    config.update(cfg_commit_comment.config)
    config.update(cfg_fork.config)
    config.update(cfg_issue_comment.config)
    config.update(cfg_issues.config)
    config.update(cfg_member.config)
    config.update(cfg_pull_request_review_comment.config)
    config.update(cfg_pull_request_review.config)
    config.update(cfg_pull_request.config)
    config.update(cfg_push.config)
    config.update(cfg_star.config)

    return config


def get_schema():
    from configs import schema as cfg_schema

    schema = cfg_schema.schema

    return schema


def fetch(key, data):
    steps = key.split('.')
    data = data.copy()
    for step in steps:
        data = data[step]
    return data


def build(total, part):
    gconfig = get_config()
    gschema = get_schema()
    cnt = 0
    for fn in glob.glob('./data/events/*.json'):
        fn_date = datetime.strptime(fn, './data/events/%Y-%m-%d-%H.json')
        inc_path = fn_date.strftime('./data/graph/_%Y-%m-%d-%H.txt')
        com_path = fn_date.strftime('./data/graph/%Y-%m-%d-%H.txt')
        if fn_date.timetuple().tm_yday % total != part or os.path.exists(com_path):
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
                                    key = fetch(
                                        entity['e']['type_field'], event)
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
                                fw.write(f"{e['type']}\t")
                                fw.write(f"/{entity['v2']['type']}/{v2['id']}\t")
                                fw.write(f"{e['created_at']}\n")

                                cnt += 1

                            if cnt % 1e5 == 0:
                                print(cnt)

            os.rename(inc_path, com_path)


if __name__ == '__main__':
    total_threads = int(os.environ('TOTAL_THREADS', '36'))
    task_id = int(os.environ('SLURM_ARRAY_TASK_ID', '-1'))
    for i in range(task_id * 2, (task_id + 1) * 2):
        t = threading.Thread(target=build, args=(total_threads, i))
        t.start()
        t.join()
