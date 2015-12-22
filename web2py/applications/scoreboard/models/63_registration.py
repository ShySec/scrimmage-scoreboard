def register_user(form, oauth=False):
	f = form.vars
	if f.create: form.errors.team = IS_NOT_IN_DB(db,db.teams.name,'team name already in use')(f.team)[1]
	else:        form.errors.team = IS_NOT_EMPTY('invalid team name or code')(db.teams(name=f.team,secret=f.code))[1]
	if form.errors.team: return

	if oauth: user = db.auth_user.insert(email=f.email,password='<oauth>',oauth_name=session.oauth)
	else:     user = db.auth_user.insert(email=f.email,password=str(CRYPT()(f.password)[0]))

	if f.create: team = register_team_owner(f.team, user, f.public_key)
	else:        team = register_team_user(f.team, user, f.public_key)
	if team: auth.login_user(db.auth_user[user.id])
	return team

def register_team_owner(team_name, user, public_key):
	team = register_new_team(team_name)
	sendmail(user.email, 'SamuraiCTF Team Registration', 'team_registration.html', dict(team=team,user=user))
	db.team_users.insert(team=team,user_id=user,public_key=public_key,role='owner')
	register_team_server(team)
	return team

def register_team_user(team_name, user, public_key):
	team = db.teams(name=team_name)
	if not team: raiseUserError(404,'invalid team name: %s',team_name)
	sendmail(user.email, 'SamuraiCTF User Registration', 'user_registration.html', dict(team=team,user=user))
	db.team_users.insert(team=team,user_id=user,public_key=public_key,role='user')
	update_team_server(team)
	return team

def register_new_team(team_name):
	secret_code = generateRandomString(40)
	team = db.teams.insert(name=team_name,host='',status='inactive',secret=secret_code)
	assign_team_services(team)
	return team

def assign_team_services(team):
	for service in db(db.services.status=='active').select():
		db.team_services.insert(team=team,service=service)

def register_team_server(team):
	db.commit() # commit before queueing to async handler
	scheduler.queue_task(task_assign_server,pvars=[team.id])
	return team

def update_team_server(team):
	db.commit() # commit before queueing to async handler
	scheduler.queue_task(task_set_team_credentials,pvars=[team.id])
	return team

def send_assignments():
	for team in db(db.teams.host!=None)(db.teams.status!='disabled').select():
		send_assignment(team=team)

def send_assignment(team):
	for owner in get_team_owners(team):
		sendmail(owner.email, 'SamuraiCTF Server Assignment', 'server_assignment.html', dict(team=team))

def send_game_start():
	for team in db(db.teams.status=='active').select():
		team_user = db.team_users(team=team)
		if not team_user: continue
		user = db.auth_user[team_user.user_id]
		sendmail(user.email, 'SamuraiCTF starts NOW', 'text.html', dict(text=XML('SamuraiCTF starting NOW!')))
