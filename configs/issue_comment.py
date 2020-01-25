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
                   'type': {
                       'created': 'U_SO_C_IC',
                       'edited': 'U_SO_E_IC',
                       'edited': 'U_SO_D_IC',
                   },
                   'type_field': 'payload.action',
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
                   'type': {
                       'created': 'IC_AO_C_I',
                       'edited': 'IC_AO_E_I',
                       'edited': 'IC_AO_D_I',
                   },
                   'type_field': 'payload.action',
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
