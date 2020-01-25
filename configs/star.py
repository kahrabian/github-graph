config = {
    'StarEvent': {
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
                       'created': 'U_HS_A_R',
                       'deleted': 'U_HS_R_R',
                   },
                   'type_field': 'payload.action',
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
