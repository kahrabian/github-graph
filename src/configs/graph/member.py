config = {
    'MemberEvent': {
        'entities': [
            {
                'v1': {
                    'type': 'user',
                    'features': {
                        'id': 'payload.member.id',
                    },
                },
                'e': {
                    'type': 'U_A_R',
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
