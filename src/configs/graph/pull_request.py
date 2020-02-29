config = {
    'PullRequestEvent': {
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
                       'assigned': 'U_SO_A_P',
                       'unassigned': 'U_SO_UA_P',
                       'review_requested': 'U_SO_RR_P',
                       'review_request_removed': 'U_SO_RRR_P',
                    #    'labeled': 'U_SO_L_P',
                    #    'unlabeled': 'U_SO_UL_P',
                       'opened': 'U_SO_O_P',
                       'edited': 'U_SO_E_P',
                       'closed': 'U_SO_C_P',
                       'ready_for_review': 'U_SO_RFR_P',
                       'locked': 'U_SO_L_P',
                       'unlocked': 'U_SO_UL_P',
                       'reopened': 'U_SO_R_P',
                       'synchronize': 'U_SO_S_P',
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
           {
               'v1': {
                   'type': 'user',
                   'features': {
                       'id': 'payload.pull_request.assignee.id',
                   },
               },
               'e': {
                   'type': {
                       'assigned': 'U_AO_A_P',
                       'unassigned': 'U_AO_U_P',
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
           {
               'v1': {
                   'type': 'user',
                   'features': {
                       'id': 'payload.pull_request.requested_reviewer.id',
                   },
               },
               'e': {
                   'type': {
                       'review_requested': 'U_RRO_A_P',
                       'review_request_removed': 'U_RRO_R_P',
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
        #    {
        #        'v1': {
        #            'type': 'commit',
        #            'features': {
        #                'id': 'payload.pull_request.base.sha',
        #            },
        #        },
        #        'e': {
        #            'type': 'C_BO_P',
        #            'features': [
        #                'created_at',
        #            ],
        #        },
        #        'v2': {
        #            'type': 'pr',
        #            'features': {
        #                'id': 'payload.pull_request.id',
        #            },
        #        },
        #    },
        #    {
        #        'v1': {
        #            'type': 'commit',
        #            'features': {
        #                'id': 'payload.pull_request.head.sha',
        #            },
        #        },
        #        'e': {
        #            'type': 'C_HO_P',
        #            'features': [
        #                'created_at',
        #            ],
        #        },
        #        'v2': {
        #            'type': 'pr',
        #            'features': {
        #                'id': 'payload.pull_request.id',
        #            },
        #        },
        #    },
           {
               'v1': {
                   'type': 'pr',
                   'features': {
                       'id': 'payload.pull_request.id',
                   },
               },
               'e': {
                   'type': {
                       'assigned': 'P_AO_A_R',
                       'unassigned': 'P_AO_UA_R',
                       'review_requested': 'P_AO_RR_R',
                       'review_request_removed': 'P_AO_RRR_R',
                    #    'labeled': 'P_AO_L_R',
                    #    'unlabeled': 'P_AO_UL_R',
                       'opened': 'P_AO_O_R',
                       'edited': 'P_AO_E_R',
                       'closed': 'P_AO_C_R',
                       'ready_for_review': 'P_AO_RFR_R',
                       'locked': 'P_AO_L_R',
                       'unlocked': 'P_AO_UL_R',
                       'reopened': 'P_AO_R_R',
                       'synchronize': 'P_AO_S_R',
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
