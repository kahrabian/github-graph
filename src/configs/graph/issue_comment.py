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
                    'type': 'U_C_IC',
                    'features': [
                        'created_at',
                    ],
                },
                'v2': {
                    'type': 'issue_comment',
                    'features': {
                        'id': 'payload.comment.id',
                    },
                },
            },
            {
                'v1': {
                    'type': 'issue_comment',
                    'features': {
                        'id': 'payload.comment.id',
                    },
                },
                'e': {
                    'type': 'IC_C_I',
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
