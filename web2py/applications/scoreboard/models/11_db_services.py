#------------------------------------------------------------------------------
#-- helpers
#------------------------------------------------------------------------------
def calc_team_total(team, field):
	service_scores = db(db.team_services.team==team.teams.id)(db.team_services.service==db.services.id)(db.services.status=='active').select(db.team_services[field])
	return sum(service[field] for service in service_scores)

def calc_team_captures(team):
	captures = db.team_service_captures
	query = db(captures.attacker==team.teams.id)(captures.defender==db.team_services.id)
	query = query(db.team_services.service==db.services.id)(db.services.status=='active')
	return query.count()

def get_attacker_name(tsc):
	captures = db.team_service_captures
	query = db(db.team_service_captures.id==tsc.team_service_captures.id)
	query = query(db.team_service_captures.defender==db.team_services.id)
	query = query(db.team_services.service==db.services.id)(db.services.status=='active')
	query = query(db.team_service_captures.attacker==db.teams.id)
	return query.select(db.teams.name).first().name

def get_defender_name(tsc):
	captures = db.team_service_captures
	query = db(db.team_service_captures.id==tsc.team_service_captures.id)
	query = query(db.team_service_captures.defender==db.team_services.id)
	query = query(db.team_services.service==db.services.id)(db.services.status=='active')
	query = query(db.team_services.team==db.teams.id)
	return query.select(db.teams.name).first().name

#------------------------------------------------------------------------------
#-- active before/during game
#------------------------------------------------------------------------------
db.define_table('services',
          Field('status',             'string',  requires=IS_IN_SET(['active','disabled'],zero=None),default='active'),
          Field('token_letters',      'string',  default='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \t'),
          Field('token_length',       'integer', default=0),
          Field('color',              'string',  default='#FFFFFF'),
          Field('port',               'integer'),
          Field('name',               'string'),
          auth.signature)

db.define_table('service_tests',
          Field('status',             'string', requires=IS_IN_SET(['active','disabled'],zero=None),default='active'),
          Field('service',            'reference services'),
          Field('filename',           'string'),
          Field('name',               'string'),
          Field('timeout',            'integer', default=0),
          auth.signature)

db.define_table('teams',
          Field('status',             'string', requires=IS_IN_SET(['inactive','assigned','active','disabled'],zero=None),default='inactive'),
          Field('simulated_server',   'boolean', default=False), # automatically passes SLA
          Field('name',               'string'),
          Field('host',               'string'),
          Field('secret',             'string'), # secret code required to join this team

  Field.Virtual('score',              lambda team:calc_team_total(team,'score')),
  Field.Virtual('captured',           lambda team:calc_team_total(team,'captured')),
  Field.Virtual('failed',             lambda team:calc_team_total(team,'failed')),
  Field.Virtual('scored',             lambda team:calc_team_total(team,'scored')),

  Field.Virtual('captures',           lambda team:calc_team_captures(team)),
          auth.signature)

db.define_table('team_server_pool',
          Field('status',             'string', requires=IS_IN_SET(['disabled','active','failed'],zero=None),default='disabled'),
          Field('contributor',        'reference auth_user'),
          Field('assigned',           'reference teams'),
          Field('address',            'string'),
          auth.signature)

db.define_table('team_services',
          Field('team',               'reference teams'),
          Field('service',            'reference services'),
          Field('score',              'integer', default=1000),
          Field('remnants',           'integer', default=0), # unclaimed points for future distribution
          Field('captured',           'integer', default=0),
          Field('failed',             'integer', default=0),
          Field('scored',             'integer', default=0),
          auth.signature)

db.define_table('team_service_tokens',
          Field('status',             'string', requires=IS_IN_SET(['active','captured','invalid'],zero=None), default='active'),
          Field('team_service',       'reference team_services'),
          Field('expires',            'datetime'),
          Field('token',              'string'),
          auth.signature)

#------------------------------------------------------------------------------
#-- active only during game
#------------------------------------------------------------------------------
db.define_table('game_rounds',
          Field('status',             'string',  requires=IS_IN_SET(['active','polling','polled','scoring','scored'],zero=None),default='active'),
          Field('starts_at',          'datetime', default=request.utcnow),
          Field('expires_at',         'datetime', default=request.utcnow+game_round_intervals()),
          Field('services',           'integer', default=0),
          Field('teams',              'integer', default=0),
          Field('captured',           'integer', default=0),
          Field('failed',             'integer', default=0),
          Field('passed',             'integer', default=0),
          auth.signature)

db.define_table('game_round_teams',
          Field('game_round',         'reference game_rounds'),
          Field('team',               'reference teams'),
          auth.signature)

db.define_table('game_round_services',
          Field('game_round',         'reference game_rounds'),
          Field('service',            'reference services'),
          Field('point_pool',         'integer'),
          auth.signature)

db.define_table('team_service_test_tokens',
          Field('game_round',         'reference game_rounds'),
          Field('service_test',       'reference service_tests'),
          Field('team_service',       'reference team_services'),
          Field('token',              'string'),
          auth.signature)

db.define_table('team_service_test_results',
          Field('game_round',         'reference game_rounds'),
          Field('service_test',       'reference service_tests'),
          Field('team_service',       'reference team_services'),
          Field('status_code',        'integer'),
          Field('stdout',             'blob'),
          Field('stderr',             'blob'),
          auth.signature)

db.define_table('team_service_captures',
          Field('game_round',         'reference game_rounds'),
          Field('defender',           'reference team_services'),
          Field('attacker',           'reference teams'),

          Field.Virtual('attacker_name', lambda tsc:get_attacker_name(tsc)),
          Field.Virtual('defender_name', lambda tsc:get_defender_name(tsc)),

          auth.signature)

db.define_table('team_captures',
          Field('status',             'string', requires=IS_IN_SET(['success','not-found','not-available','not-active'],zero=None)),
          Field('game_round',         'reference game_rounds'),
          Field('submitter',          'reference teams'),
          Field('token',              'string'),
          auth.signature)

db.define_table('team_service_round_result',
          Field('game_round',         'reference game_rounds'),
          Field('service',            'reference services'),
          Field('team',               'reference teams'),
          Field('result',             'string', requires=IS_IN_SET(['passed','failed','captured'],zero=None)),
          auth.signature)
