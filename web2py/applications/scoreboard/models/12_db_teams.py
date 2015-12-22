'''
db.define_table('teams',
          Field('status',             'string', requires=IS_IN_SET(['active','disabled'],zero=None),default='active'),
          Field('name',               'string'),
          Field('host',               'string'),
          auth.signature)
'''

db.define_table('team_users',
          Field('team',               'reference teams'),
          Field('user_id',            'reference auth_user'),
          Field('role',               'string', requires=IS_IN_SET(['owner','user'])),
          Field('public_key',         'text'),
          auth.signature)
