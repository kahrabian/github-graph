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
                   'type': {
                       'created': 'U_SO_C_PRC',
                       'edited': 'U_SO_E_PRC',
                       'edited': 'U_SO_D_PRC',
                   },
                   'type_field': 'payload.action',
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
                   'type': {
                       'created': 'PRC_AO_C_P',
                       'edited': 'PRC_AO_E_P',
                       'edited': 'PRC_AO_D_P',
                   },
                   'type_field': 'payload.action',
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
