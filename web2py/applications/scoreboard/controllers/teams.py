grid_kwargs = dict(csv=False, create=False, deletable=False, editable=False, searchable=False, details=False)

def index():
	requireSSL()
	headers = {'teams.name':'Team','teams.scored':'Passed','teams.captured':'Lost','teams.captures':'Stole Flag'}
	fields = map(lambda x:db.teams[x],['name','score','scored','failed','captured','captures'])
	if isGameActive() and auth.user: fields.insert(1,db.teams.host)
	links = [dict(header='',body=lambda row:A(BUTTON('Details'),_href=URL('view',vars=dict(id=row.id))))]

	query = (db.teams.status=='active')
	if auth.user:
		user_team = db.team_users(user_id=auth.user.id)
		if user_team: query |= (db.teams.id==user_team.team)
	if isAdmin():
		query = (db.teams)
	form = SQLFORM.grid(query=query,fields=fields,links=links,headers=headers,orderby=db.teams.name|db.teams.id, **grid_kwargs)
	return dict(form=form)

def view():
	requireSSL()
	team = lookupVarID('id',db.teams)
	if not team: raiseUserError(400,'attempted access to missing team: %s',request.vars)

	headers = {'services.name':'Service','teams.name':'Team'}
	query = ((db.team_services.team==team)&(db.team_services.service==db.services.id)&(db.services.status=='active'))
	fields = [db.services.name,db.team_services.score,db.team_services.scored,db.team_services.failed,db.team_services.captured]
	form = SQLFORM.grid(query=query,fields=fields,headers=headers,orderby=db.services.name, **grid_kwargs)

	users = None
	if is_team_owner() or isAdmin():
		users = db(db.team_users.team==team)(db.team_users.user_id==db.auth_user.id).select(db.auth_user.email)

	round_data = []
	latest_rounds = db(db.game_rounds.status=='scored').select(orderby=~db.game_rounds.id,limitby=(0,3))
	for game_round in latest_rounds:
		headers = {'services.name':'Service'}
		fields = [db.services.name,db.team_service_round_result.result]
		query  = (db.team_service_round_result.game_round==db.game_rounds.id)
		query &= (db.team_service_round_result.service==db.services.id)
		query &= (db.team_service_round_result.team==db.teams.id)
		query &= (db.game_rounds.id==game_round.id)
		query &= (db.services.status=='active')
		query &= (db.teams.status=='active')
		query &= (db.teams.id==team.id)
		round_form = SQLFORM.grid(query=query,fields=fields,headers=headers,orderby=db.services.name,**grid_kwargs)
		round_data.append((game_round.id,round_form))
	return dict(team=team,form=form,round_data=round_data,users=users)

def register():
	requireSSL()
	password_validator = IS_LENGTH(256,9,'please enter a 9+ character password')
	confirm_validator = IS_EQUAL_TO(request.vars.password,'passwords don\'t match')

	email_validators = [IS_EMAIL('please enter a valid email address'),IS_NOT_IN_DB(db,db.auth_user.email,'email address already in use')]
	team_validators = [IS_ALPHANUMERIC('please enter an alphanumeric team name'),IS_LENGTH(128,4,'please enter a 4+ character team name')]

	host_validators = [IS_IPV4(error_message='please enter a valid IPv4 address in dotted decimal form', is_localhost=False, is_private=False, is_automatic=False),
	                   IS_NOT_IN_DB(db,db.teams.host,'server address already in use')]

	pubkey_validators = IS_EMPTY_OR([IS_PUBLIC_KEY(),IS_NOT_IN_DB(db,db.team_users.public_key,'public key already in use')])

	table = TABLE(TR(LABEL('Email Address'),      INPUT(_name='email',      _class='email',    requires=email_validators)),
	              TR(LABEL('Password'),           INPUT(_name='password',   _class='password', requires=password_validator, _placeholder='9+ characher password',_type='password')),
	              TR(LABEL('Verify Password'),    INPUT(_name='verify',     _class='password', requires=confirm_validator,  _placeholder='retype your password from above',  _type='password')),
	              TR(TD(_colspan="2",_class='divider')),
	              TR(LABEL('Public Key'),         TEXTAREA(_name='public_key',  requires=pubkey_validators, _placeholder='ssh public key')),
	              TR(TD(_colspan="2",_class='divider')),
	              TR(LABEL('Team Name'),          INPUT(_name='team',       _class='team',     requires=team_validators,    _placeholder='team name for scrimmage')),
	              TR(TD(_colspan="2",_class='divider')),
	              TR(LABEL('Create Team'),   SPAN(INPUT(_name='create',  _type='checkbox'),
	                                         SPAN(INPUT(_name='code',    _class='code',    _placeholder='code required to join this team'), _class='toggled'))),
	              )
	register = TR(TD(
		INPUT(_type='submit', _value='Register',_class='btn btn-success btn-lg'),
		A(INPUT(_type='button', _value='Github',  _class='btn btn-success btn-lg'),_href='/github/register'),
		_colspan="2",_style="padding-top: 5px; text-align: center;"))
	table.append(register)
	form = FORM(table)

	if form.validate(keepvalues=True):
		logUserInfo('new user (%s) registering for %s',form.vars.email,form.vars.team)
		if not register_user(form):
			response.flash = 'Errors in form, please check it out.'
		else:
			session.flash = 'Welcome to the Samurai Scrimmage'
			redirect(URL('teams','index'))
	return dict(form=form)

@auth.requires_login()
def generate_certificate():
	requireSSL()
	import hashlib
	import subprocess
	team = get_user_team()
	if not team:
		session.flash = 'Certificate generation failed as you have no team. Please contact support for assistance.'
		emailUserError('player on missing team')
		redirect('/teams')

	status = -1
	path = '/home/ctf/scoreboard'
	command = map(str,['./create_client_certificate',team.name,auth.user.email])
	logUserDebug('command = %s',command)
	try:
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path)
		stdout,stderr = process.communicate()
		status = process.returncode
		certificate = stdout
	except:
		logUserException('failed to create certificate (%d): %s',status,command)
	if status:
		logUserError('failed to create certificate (%d): %s\nstdout: %s\nstderr: %s',status,command,stdout,stderr)
		session.flash = 'Certificate generation failed. Please contact support for assistance.'
		redirect('/teams')
	logUserInfo('certificate: %s',hashlib.sha256(certificate).hexdigest())
	return dict(certificate=certificate)
