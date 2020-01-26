config = {
    'PullRequestReviewEvent': {
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
                       'submitted': 'U_SO_S_PR',
                       'edited': 'U_SO_E_PR',
                       'dismissed': 'U_SO_D_PR',
                   },
                   'type_field': 'payload.action',
                   'features': [
                       'created_at',
                   ],
               },
               'v2': {
                   'type': 'pr_review',
                   'features': {
                       'id': 'payload.review.id',
                   },
               },
           },
           {
               'v1': {
                   'type': 'pr_review',
                   'features': {
                       'id': 'payload.review.id',
                   },
               },
               'e': {
                   'type': 'C_O_PR',
                   'features': [
                       'created_at',
                   ],
               },
               'v2': {
                   'type': 'commit',
                   'features': {
                       'id': 'payload.review.commit_id',
                   },
               },
           },
           {
               'v1': {
                   'type': 'pr_review',
                   'features': {
                       'id': 'payload.review.id',
                   },
               },
               'e': {
                   'type': {
                       'submitted': 'PR_AO_S_P',
                       'edited': 'PR_AO_E_P',
                       'dismissed': 'PR_AO_D_P',
                   },
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
