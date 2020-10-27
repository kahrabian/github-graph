config = {
    'PullRequestEvent': {
        'entities': [
            {
                'v1': {
                    'type': 'user',
                    'features': {
                        'id': 'actor.id',
                    },
                },
                'e': {
                    'type': {
                        'opened': 'U_O_P',
                        'closed': 'U_C_P',
                        'reopened': 'U_R_P',
                    },
                    'type_field': 'payload.action',
                    'features': [
                        'created_at',
                        'payload.pull_request.merged'
                    ],
                },
                'v2': {
                    'type': 'pr',
                    'features': {
                        'id': 'payload.pull_request.id',
                    },
                },
            },
            {
                'v1': {
                    'type': 'pr',
                    'features': {
                        'id': 'payload.pull_request.id',
                    },
                },
                'e': {
                    'type': {
                        'opened': 'P_O_R',
                        'closed': 'P_C_R',
                        'reopened': 'P_R_R',
                    },
                    'type_field': 'payload.action',
                    'features': [
                        'created_at',
                        'payload.pull_request.merged'
                    ],
                },
                'v2': {
                    'type': 'repo',
                    'features': {
                        'id': 'repo.id',
                    },
                },
            },
        ],
    },
}
