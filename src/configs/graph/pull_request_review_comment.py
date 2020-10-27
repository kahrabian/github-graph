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
        ],
    },
}
