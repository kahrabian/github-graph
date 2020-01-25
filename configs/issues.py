config = {
    'IssuesEvent': {
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
                       'opened': 'U_SE_O_I',
                       'edited': 'U_SE_E_I',
                       'deleted': 'U_SE_D_I',
                       'pinned': 'U_SE_P_I',
                       'unpinned': 'U_SE_UP_I',
                       'closed': 'U_SE_C_I',
                       'reopened': 'U_SE_RO_I',
                       'assigned': 'U_SE_A_I',
                       'unassigned': 'U_SE_UA_I',
                    #    'labeled': 'U_SE_L_I',
                    #    'unlabeled': 'U_SE_UL_I',
                       'locked': 'U_SE_LO_I',
                       'unlocked': 'U_SE_ULO_I',
                       'transferred': 'U_SE_T_I',
                    #    'milestoned': 'U_SE_M_I',
                    #    'demilestoned': 'U_SE_DM_I',
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
           {
               'v1': {
                   'type': 'user',
                   'features': {
                       'id': 'payload.assignee.id',
                   },
               },
               'e': {
                   'type': {
                       'assigned': 'U_AO_A_I',
                       'unassigned': 'U_AO_UA_I',
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
           {
               'v1': {
                   'type': 'issue',
                   'features': {
                       'id': 'payload.issue.id',
                   },
               },
               'e': {
                   'type': {
                       'opened': 'I_AO_O_R',
                       'edited': 'I_AO_E_R',
                       'deleted': 'I_AO_D_R',
                       'pinned': 'I_AO_P_R',
                       'unpinned': 'I_AO_UP_R',
                       'closed': 'I_AO_C_R',
                       'reopened': 'I_AO_RO_R',
                       'assigned': 'I_AO_A_R',
                       'unassigned': 'I_AO_UA_R',
                    #    'labeled': 'I_AO_L_R',
                    #    'unlabeled': 'I_AO_UL_R',
                       'locked': 'I_AO_LO_R',
                       'unlocked': 'I_AO_ULO_R',
                       'transferred': 'I_AO_T_R',
                    #    'milestoned': 'I_AO_M_R',
                    #    'demilestoned': 'I_AO_DM_R',
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
