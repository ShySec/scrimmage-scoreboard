grid_kwargs = dict(csv=False, create=False, deletable=False, editable=False, searchable=False, details=False)

def recent_round():
	last_round = db(db.game_rounds.status=='scored').select(orderby=~db.game_rounds.id,limitby=(0,1)).first()
	if not last_round: last_round = db(db.game_rounds).select(orderby=~db.game_rounds.id,limitby=(0,1)).first()
	if last_round: redirect(URL('view',vars=dict(id=last_round.id)))
	redirect(URL('index'))

def index():
	headers = {'game_rounds.id':'Round'}
	query = (db.game_rounds.status=='scored')
	fields = map(lambda x:db.game_rounds[x],['id','passed','failed','captured'])
	links = [dict(header='',body=lambda row:A(BUTTON('Details'),_href=URL('view',vars=dict(id=row.id))))]
	form = SQLFORM.grid(query=query,fields=fields,headers=headers,links=links,orderby=~db.game_rounds.id, **grid_kwargs)
	return dict(form=form)

def view():
	game_round = lookupVarID('id',db.game_rounds)
	if not game_round: return 'uh-uh'
	if game_round.status != 'scored' and not isAdmin():
		return 'uh-uh'

	headers = {'services.name':'Service','teams.name':'Team'}
	test_orderby=db.services.name|db.service_tests.name|db.team_service_test_results.id
	fields = [db.services.name,db.teams.name,db.service_tests.name]

	query  = (db.team_service_test_results.game_round==game_round)
	query &= (db.team_service_test_results.service_test==db.service_tests.id)
	query &= (db.team_service_test_results.team_service==db.team_services.id)
	query &= (db.team_services.team==db.teams.id)&(db.team_services.service==db.services.id)

	pass_query = query&(db.team_service_test_results.status_code==0)
	pass_results = SQLFORM.grid(query=pass_query,fields=fields,headers=headers,orderby=test_orderby, **grid_kwargs)

	fail_query = query&(db.team_service_test_results.status_code!=0)
	fail_results = SQLFORM.grid(query=fail_query,fields=fields,headers=headers,orderby=test_orderby, **grid_kwargs)

	db.team_service_captures.id.readable=False
	query  = (db.team_service_captures.game_round==game_round)
	query &= (db.team_service_captures.defender==db.team_services.id)
	query &= (db.team_services.id==db.team_service_captures.defender)
	query &= (db.team_services.team==db.teams.id)&(db.team_services.service==db.services.id)
	fields = [db.team_service_captures.id,db.services.name,db.team_service_captures.attacker_name,db.team_service_captures.defender_name]
	captures = SQLFORM.grid(query=query,fields=fields,headers=headers,orderby=db.services.name|db.team_service_captures.id,**grid_kwargs)
	return dict(game_round=game_round,pass_results=pass_results,fail_results=fail_results,captures=captures)
