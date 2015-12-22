def task_enable_service(service=None, name=None):
	if service is None and name: service = db.services(name=name)
	if not service: return logger.error('invalid service')
	logger.info('enabling service %s',service.name)
	service.update_record(status='active')
	for team in db(db.teams.status=='active').select():
		if db.team_services(team=team,service=service): continue
		db.team_services.insert(team=team,service=service)
	db.commit()
	return True

def task_disable_service(service=None, name=None):
	if service is None and name: service = db.services(name=name)
	if not service: return logger.error('invalid service')
	logger.info('disabling service %s',service.name)
	service.update_record(status='disabled')
	db.commit()
	return True

def task_reenable_services():
	logger.info('reenabling all team services')
	for team in db(db.teams.status=='active').select():
		for service in db(db.services.status=='active').select():
			if db.team_services(team=team,service=service): continue
			db.team_services.insert(team=team,service=service)
	db.commit()
	return True

def task_disable_all_services():
	logger.info('disabling all services')
	for service in db(db.services.status=='active').select():
		service.update_record(status='disabled')
	db.commit()
	return True

def task_reset_round_scoring():
	logger.debug('resetting all service scores to initial game state')
	db(db.team_service_round_result).delete()
	db(db.team_services).update(score=1000,remnants=0,captured=0,failed=0,scored=0)
	for game_round in db(db.game_rounds.status=='scored').select():
		game_round.update_record(status='polled',captured=0,failed=0,passed=0)
		db.game_round_services(game_round=game_round).update_record(point_pool=0)
	logger.info('reset all services to pre-scored state')
	db.commit()

def task_explain_token(token):
	logUserDebug('explaining %s',token)
	team_service = db(db.team_service_tokens.token==token).select()
	if not len(team_service):
		logUserError('invalid token')
		return 'no such token'
	if len(team_service)>1:
		logUserError('token found across multiple (%d) team_services: %s',len(team_service),token)
	team_service = team_service.first().team_service
	service=team_service.service
	team=team_service.team

	retval = []
	for capture in db(db.team_captures.token==token).select(orderby=db.team_captures.game_round):
		entry = dict(game_round=capture.game_round.id,service=service.name,defender=team.name,attacker=capture.submitter.name)
		ts_round_result = db.team_service_round_result(game_round=capture.game_round,service=service,team=team)
		if not ts_round_result: entry['status']='unscored'
		else: entry['status']=ts_round_result.result
		retval.append(entry)
	logUserDebug('reporting %d captures',len(retval))
	return retval

def task_explain_tokens(tokens):
	return dict([(token,task_explain_token(token)) for token in tokens])
