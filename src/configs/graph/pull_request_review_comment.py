config = {
    'PullRequestReviewCommentEvent': {
        'entities': [
            {
                'v1': {
                    'type': 'user',
                    'features': {
                        'id': 'actor.id',
                    },
                },
                'e': {
                    'type': 'U_CO_P',
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
        ],
    },
}
