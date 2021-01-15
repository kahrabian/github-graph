config = {
    'IssueCommentEvent': {
        'entities': [
            {
                'v1': {
                    'type': 'user',
                    'features': {
                        'id': 'actor.id',
                    },
                },
                'e': {
                    'type': 'U_CO_I',
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
        ],
    },
}
