def get_oauth_name(user):
	if not user: return
	user_id = str(user.get('id',''))
	if not user_id: return
	if not IS_LENGTH(128,1)(user_id)[0]: return
	if not IS_ALPHANUMERIC()(user_id)[0]: return
	return '%s@github.com'%user_id

def get_user_email(user):
	if not user: return
	email = user.get('email','')
	if not IS_EMAIL()(email)[0]: return
	if not IS_LENGTH(128,3)(email)[0]: return
	return email

def get_best_email(emails):
	if not emails: return
	invalid_domain = 'users.noreply.github.com'
	emails = filter(lambda x:IS_EMAIL()(x.get('email',''))[0],emails)
	emails = filter(lambda x:not x.get('email','').endswith(invalid_domain),emails)
	verified_emails = filter(lambda x:x.get('verified',False),emails)
	primary_emails = filter(lambda x:x.get('primary',False),verified_emails)
	if len(primary_emails): return primary_emails[0].get('email')
	if len(verified_emails): return verified_emails[0].get('email')
	if len(emails): return emails[0].get('email')
	return

def get_user_login(user):
	if not user: return
	login = user.get('login','')
	if not IS_ALPHANUMERIC()(login)[0]: return
	if not IS_LENGTH(128,4)(login)[0]: return
	return login

def get_public_key(keys):
	if not keys: return
	return '\n'.join(filter(lambda x:x,[key.get('key','') for key in keys]))

def extract_github_details(ga):
	user = None
	keys = None
	email = None
	if not session.oauth:
		if not user: user = ga.get_user()
		session.oauth = get_oauth_name(user)
		logUserDebug('oauth = %s',session.oauth)
	if not session.oauth:
		logUserError('unusable github response: %s',user)
		session.flash = 'unable to verify identity through Github'
		redirect('/teams/register')
	if db.auth_user(oauth_name=session.oauth):
		logUserDebug('account already exists; redirecting to login')
		session.flash = 'account already exists; logging in...'
		redirect(URL('github','login'))

	if not session.email:
		if not user: user = ga.get_user()
		session.email = get_user_email(user)
		logUserDebug('email = %s',session.email)
	if not session.email:
		if not email: email = ga.get_email()
		session.email = get_best_email(email)
		logUserDebug('email = %s',session.email)
	if not session.team:
		if not user: user = ga.get_user()
		session.team = get_user_login(user)
		logUserDebug('team = %s',session.team)
	if not session.public_key:
		if not keys: keys = ga.get_public_keys()
		session.public_key = get_public_key(keys)
		logUserDebug('public_key = %s',session.public_key)

def login():
	import github # we only need user:email at this point, but changing scope spawns redirects user
	ga=github.GithubAccount('user:email,read:public_key',URL('github','login'),**GithubAPI())
	guser = ga.get_user()
	oauth = get_oauth_name(guser)

	user = db.auth_user(oauth_name=oauth) if oauth else None
	if not user:
		if oauth: logUserError('invalid oauth_name: %s (%s)',oauth,guser)
		session.flash = 'unable to verify identity through Github'
		redirect('/default/user/login?_next=/teams/index')
	auth.login_user(user)
	redirect(URL('teams','index'))

def register():
	import github
	ga=github.GithubAccount('user:email,read:public_key',URL('github','register'),**GithubAPI())
	extract_github_details(ga)

	email_validators =[IS_EMAIL('please enter a valid email address'),IS_NOT_IN_DB(db,db.auth_user.email,'email address already in use')]
	team_validators = [IS_ALPHANUMERIC('please enter an alphanumeric team name'),IS_LENGTH(128,4,'please enter a 4+ character team name')]
	host_validators = [IS_IPV4(error_message='please enter a valid IPv4 address in dotted decimal form', is_localhost=False, is_private=False, is_automatic=False),
	                   IS_NOT_IN_DB(db,db.teams.host,'server address already in use')]
	pubkey_validators = [IS_MATCH('ssh-.{30,1000}','please enter a valid RSA public key'),IS_NOT_IN_DB(db,db.team_users.public_key,'public key already in use')]
	if IS_IN_DB(db,db.teams.name)(session.team)[1]==None: del session.team
	if IS_IN_DB(db,db.auth_user.email)(session.email)[1]==None: del session.email
	if IS_IN_DB(db,db.team_users.public_key)(session.public_key)[1]==None: del session.public_key

	table = TABLE()
	table.append(TR(LABEL('Email Address'),  INPUT(_name='email',     _class='email',    requires=email_validators, value=session.email)))
	table.append(TR(TD(_colspan="2",_class='divider')))
	table.append(TR(LABEL('Team Name'),      INPUT(_name='team',      _class='team',     requires=team_validators,  value=session.team,  _placeholder='team name for scrimmage')))
	table.append(TR(LABEL('Create Team'),    SPAN(INPUT(_name='create',  _type='checkbox'),
	                                         SPAN(INPUT(_name='code',    _class='code',    _placeholder='code required to join this team'), _class='toggled'),
	                                         )))
	if not session.public_key:
		table.append(TR(TD(_colspan="2",_class='divider')))
		table.append(TR(LABEL('Public Key'),     TEXTAREA(_name='public_key', _class='pubkey',   requires=pubkey_validators, value=session.public_key, _placeholder='missing or invalid public key')))

	register = TR(TD(INPUT(_type='submit', _value='Register',_class='btn btn-success btn-lg'),_colspan="2",_style="padding-top: 5px; text-align: center;"))
	table.append(register)
	form = FORM(table)

	if form.validate(keepvalues=True):
		logUserInfo('new user (%s) registering for %s',form.vars.email,form.vars.team)
		if not register_user(form,oauth=True):
			response.flash = 'Errors in form, please check it out.'
		else:
			session.flash = 'Welcome to the Samurai Scrimmage'
			redirect(URL('teams','index'))
	return response.render('teams/register.html',dict(form=form))
