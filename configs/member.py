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
                   'type': {
                       'added': 'U_CO_A_R',
                       'removed': 'U_CO_E_R',
                       'edited': 'U_CO_R_R',
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
