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
                    'type': 'U_C_PRC',
                    'features': [
                        'created_at',
                    ],
                },
                'v2': {
                    'type': 'pr_review_comment',
                    'features': {
                        'id': 'payload.comment.id',
                    },
                },
            },
            {
                'v1': {
                    'type': 'pr_review_comment',
                    'features': {
                        'id': 'payload.comment.id',
                    },
                },
                'e': {
                    'type': 'PRC_C_P',
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
