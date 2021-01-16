config = {
    'IssuesEvent': {
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
                        'opened': 'U_O_I',
                        'closed': 'U_C_I',
                        'reopened': 'U_R_I',
                    },
                    'type_field': 'payload.action',
                    'features': [
                        'created_at',
                    ],
                },
                'v2': {
                    'type': 'issue',
                    'features': {
                        'id': 'payload.issue.id',
                    },
                },
            },
            {
                'v1': {
                    'type': 'issue',
                    'features': {
                        'id': 'payload.issue.id',
                    },
                },
                'e': {
                    'type': 'I_R',
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
