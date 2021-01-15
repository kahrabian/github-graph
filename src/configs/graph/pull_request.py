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
                    'type': 'P_R',
                    'features': [
                        'created_at',
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
