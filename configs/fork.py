config = {
    'ForkEvent': {
       'entities': [
           {
               'v1': {
                   'type': 'repo',
                   'features': {
                       'id': 'payload.forkee.id',
                   },
               },
               'e': {
                   'type': 'R_FO_R',
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
