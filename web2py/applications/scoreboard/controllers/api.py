def game_round_from_request(request):
	if len(request.args)>0:
		return safeLookupID(request.args[0],db.game_rounds)
	if 'game_round' in request.vars:
		return lookupVarID('game_round',db.game_rounds,request=request)
	return get_game_round()

@auth.requires_x509_certificate()
def teams():
	game_round = game_round_from_request(request)
	if not game_round: raise_json_response(dict(error='game not active'))
	logUserDebug('downloading teams for round %d',game_round.id)
	teams = db(db.game_round_teams.game_round==game_round)(db.game_round_teams.team==db.teams.id)
	if request.vars.filtered: teams = teams(db.teams.simulated_server==False)
	teams = teams.select(db.teams.ALL)
	packager = lambda team:dict(name=team.name,host=team.host)
	return dict(teams=map(packager,teams))

@auth.requires_x509_certificate()
def services():
	game_round = game_round_from_request(request)
	if not game_round: raise_json_response(dict(error='game not active'))
	logUserDebug('downloading services for round %d',game_round.id)
	services = db(db.game_round_services.game_round==game_round)(db.game_round_services.service==db.services.id).select(db.services.ALL)
	packager = lambda service:dict(name=service.name,port=service.port)
	return dict(services=map(packager,services))

@auth.requires_x509_certificate()
def game_round():
	logUserDebug('downloading game round')
	if not isGameActive(): raise_json_response(dict(error='game not active'))
	game_round=get_game_round()
	if not game_round: raise_json_response(dict(error='game not active'))
	game_round=extract(game_round,['id','starts_at','expires_at','teams','services'])
	game_round['number'] = game_round.pop('id')
	game_round=dict(map(lambda p:(p[0],str(p[1])),game_round.iteritems()))
	return dict(game_round=game_round)
