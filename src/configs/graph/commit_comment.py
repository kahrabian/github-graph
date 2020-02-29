config = {
    'CommitCommentEvent': {
       'entities': [
           {
               'v1': {
                   'type': 'user',
                   'features': {
                       'id': 'actor.id',
                   },
               },
               'e': {
                   'type': 'U_AO_CC',
                   'features': [
                       'created_at',
                   ],
               },
               'v2': {
                   'type': 'commit_comment',
                   'features': {
                       'id': 'payload.comment.id',
                   },
               },
           },
        #    {
        #        'v1': {
        #            'type': 'commit_comment',
        #            'features': {
        #                'id': 'payload.comment.id',
        #            },
        #        },
        #        'e': {
        #            'type': 'CC_O_C',
        #            'features': [
        #                'created_at',
        #            ],
        #        },
        #        'v2': {
        #            'type': 'commit',
        #            'features': {
        #                'id': 'payload.comment.commit_id',
        #            },
        #        },
        #    },
       ],
    },
}
