config = {
    'WatchEvent': {
        'entities': [
            {
                'v1': {
                    'type': 'user',
                    'features': {
                        'id': 'actor.id',
                    },
                },
                'e': {
                    'type': 'U_W_R',
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
