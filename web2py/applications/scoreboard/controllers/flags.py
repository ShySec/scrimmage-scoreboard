requireSSL()

def index():
	return dict()

@auth.requires_x509_login()
def capture():
	token = request.body.read()
	if not token: raw_response('invalid 0-byte token')
	if len(token)!=40: raw_response('invalid %d-byte token'%len(token))
	logUserDebug('submitting token: %s',token)

	game_round = get_game_round()
	if not game_round:
		logUserError('game not active')
		raw_response('error: Game not active')

	attacker = get_user_team()
	if not attacker:
		logUserError('invalid team: %s',token)
		raw_response('error: Invalid team')

	service_token = db.team_service_tokens(token=token)
	if not service_token:
		logUserError('invalid service token: %s',token)
		raw_response("error: Token doesn't exist")

	defender = service_token.team_service.team
	service  = service_token.team_service.service

	if attacker.id == defender.id:
		logUserError("capturing own flag: %s",attacker.name)
		raw_response("error: Can't redeem your own tokens")

	prior = db.team_service_captures(game_round=game_round,attacker=attacker,defender=service_token.team_service)
	if prior is not None:
		logUserError("capturing a second flag this round (%s => %s:%s)",attacker.name,defender.name,service.name)
		raw_response("error: Already captured that team's service this round")

	status = score_team_submission(game_round, service_token, attacker)
	logUserDebug('round %d: %s stole %s from %s => %s',game_round.id,attacker.name,service.name,defender.name,status)
	if status == 'success': websocket_pwn(attacker, defender, service)
	db.team_captures.insert(game_round=game_round,submitter=attacker,token=token,status=status)
	raw_response(status)

def score_team_submission(game_round, service_token, attacker):
	if service_token is None:
		return "error: Token doesn't exist"
	if service_token.expires < request.utcnow:
		return "error: Token too old"
	if db.team_captures(game_round=game_round,submitter=attacker,token=service_token.token):
		return "error: Already redeemed that token"

	team_service = service_token.team_service
	service_token.update_record(status='captured')
	db.team_service_captures.insert(game_round=game_round,defender=team_service,attacker=attacker)
	return 'success'

def call():
	return service()

@service.json
@auth.requires_x509_certificate()
def validate():
	data = request.body.read()
	if not data: return 'certificate validated\n'
	return '%d-byte upload validated\n'%len(data)

@auth.requires_x509_certificate('samurai','rotator')
def upload():
	import json
	data = request.body.read()
	logUserDebug('%d-bytes uploaded',len(data))
	try:
		tokens = json.loads(data)
	except:
		logUserException('data=%s',data)
		return ''
	if len(tokens)>10000: raiseUserError(404,'excessive token count: %s',tokens)
	expires = datetime.utcnow()+2*game_round_intervals()
	for token in tokens:
		if not token.get('token'):
			logUserError('invalid token: %s',token)
			continue
		team = db.teams(name=token.get('team'))
		service = db.services(name=token.get('service'))
		if not team or not service:
			logUserError('invalid team/service: %s',token)
			continue
		team_service = db.team_services(service=service,team=team)
		if not team_service:
			logUserError('invalid team_service: team %s - service %s',team.name,service.name)
			continue
		db.team_service_tokens.insert(team_service=team_service,token=token.get('token'),expires=expires)
	logUserInfo('rotated %d tokens',len(tokens))
	return ''

@auth.requires_x509_certificate('samurai','rotator')
def failures():
	import json
	data = request.body.read()
	logUserDebug('%d-bytes fialures received',len(data))
	try:
		failures = json.loads(data)
	except:
		logUserException('data=%s',data)
		return ''
	for token in failures:
		if not token.get('token'):
			logUserError('invalid token: %s',token)
			continue
		ts_token = db.team_service_tokens(token=token.get('token'))
		if not ts_token:
			logUserError('invalid token: %s',token)
			continue
		ts_token.update_record(status='invalid')
	logUserInfo('rejected %d tokens',len(failures))
	return ''

@auth.requires_x509_certificate()
def explain():
	token = getVarString('token')
	raise_json_response(task_explain_token(token))
