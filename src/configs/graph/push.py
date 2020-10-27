config = {
    'PushEvent': {
        'entities': [
            {
                'v1': {
                    'type': 'user',
                    'features': {
                        'id': 'actor.id',
                    },
                },
                'e': {
                    'type': 'U_P_R',
                    'features': [
                        'created_at',
                        'payload.distinct_size'
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
