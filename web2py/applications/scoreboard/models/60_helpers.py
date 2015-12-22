def generateRandomString(length=16):
	import random, string
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))

def generate_service_token(team_service):
	return generateRandomString(40)

def userref(user=None):
	if user is None: user = auth.user
	if not user:       return 'guest [%s]'%request.env.remote_addr
	if not user.email: return 'unregistered (user %d) [%s]'%(auth.user,request.env.remote_addr)
	return '%s (user %d) [%s]'%(user.email,user.id,request.env.remote_addr)

def logUser(value, *args):      logUserDebug(value, *args)
def logUserDebug(value, *args): logger.debug(userref()+' '+value,*args)
def logUserInfo(value, *args):  logger.info( userref()+' '+value,*args)
def logUserError(value, *args): logger.error(userref()+' '+value,*args)
def logUserException(value, *args): logger.exception(userref()+' '+value,*args)

def raiseUserError(code, value, *args, **kwargs):
	logUserError(value, *args)
	raise HTTP(code,**kwargs)

def raiseUserException(code, value, *args, **kwargs):
	logUserException(value, *args)
	raise HTTP(code,**kwargs)

def flashUserError(code, message, *args):
	session.flash = message%args if len(args) else message
	raiseUserError(code, session.flash)

def flashUserException(code, message, *args):
	session.flash = message%args if len(args) else message
	raiseUserException(code, session.flash)

def raw_response(data, *args):
	if not data.endswith('\n'): data += '\n'
	if len(args): data %= args
	raise HTTP(200,data)

def raise_json_response(data):
	import json
	raise HTTP(200,json.dumps(data)+'\n')

def safeLookupID(id, table, default=None, error=None):
	try:
		id = int(id)
	except:
		logUserError('invalid ID "%s" for table %s',id,table._tablename)
		if error: raise HTTP(error)
		return default
	try:
		retval = table[id]
	except:
		logUserError('exception on ID %d lookup from table %s',id,table._tablename)
		if error: raise HTTP(error)
		return default
	if retval is None:
		logUserError('ID %d not in table %s',id,table._tablename)
		if error: raise HTTP(error)
		return default
	return retval

def getVarString(var, default=None):  return request.vars.get(var,default)

def lookupVarID(var, table, default=None, error=None, request=request):
	id = request.vars.get(var,None)
	if id is not None: return safeLookupID(id,table,default,error=error)
	if error: raiseUserError(error,'missing required ID var "%s"',var)
	return default

def assignWeb2pyGlobals():
	import __builtin__ as b
	b.web2py = Storage(globals())
	b.logger = logger
	b.db = db

def get_user_teams(user=None):
	if user is None: user = auth.user
	return db(db.team_users.user_id==user)(db.team_users.team==db.teams.id).select(db.teams.ALL)

def get_user_team(user=None):
	if user is None: user = auth.user
	return get_user_teams(user).first()

def sendmail(to, subject, template, message, **kwargs):
	if myconf.take('email.enabled') != 1: return
	if isDebug(): subject = '[DEBUG] '+subject
	try:
		m = mail.send(to=to,subject=subject, message=response.render('emails/%s'%template,**message),**kwargs)
		if not m: logger.error('failed to send email to %s (subj: %s) -> %s :: %s'%(to,subject,mail.error,mail.result))
		else: logger.info('sent email to %s (subj: %s)'%(to,subject))
		return m
	except:
		logger.exception('failed to send email to %s (subj: %s)'%(to,subject))

def emailUserError(value, *args):
	logUserError(value, *args)
	message = dict(user=userref(),message=((userref()+' '+value)%args),traceback='')
	return sendmail(to=myconf.take('email.support'),subject='Scoreboard Error',template='internal/email_error.html',message=message)

def emailUserException(value, *args):
	import traceback
	logUserException(value, *args)
	message = dict(user=userref(),message=((userref()+' '+value)%args),traceback=traceback.format_exc())
	return sendmail(to=myconf.take('email.support'),subject='Scoreboard Exception',template='internal/email_error.html',message=message)

def get_game_round():
	if not isGameActive(): return
	query = db(db.game_rounds.starts_at<=request.utcnow)(db.game_rounds.expires_at>=request.utcnow)
	game_round = query.select(limitby=(0,1),orderby=~db.game_rounds.id).first()
	if not game_round: game_round = start_game_round()
	return game_round

def start_game_round():
	if not isGameActive(): return
	teams = db(db.teams.status=='active').select()
	services = db(db.services.status=='active').select()
	if not len(teams): return logger.debug('waiting on teams to start game round')
	if not len(services): return logger.debug('waiting on services to start game round')
	logger.debug('starting new game round')

	game_round_id = db.game_rounds.insert(status='active',services=len(services),teams=len(teams))
	for team in teams:
		db.game_round_teams.insert(game_round=game_round_id,team=team)
	for service in services:
		point_pool = 0
		query = db(db.game_rounds.status=='scored')(db.game_rounds.id==db.game_round_services.game_round)
		query = query(db.game_round_services.service==service)(db.game_round_services.point_pool>0)
		for service_point_pool in query.select(db.game_round_services.ALL):
			point_pool += service_point_pool.point_pool
			service_point_pool.update_record(point_pool=0)
		db.game_round_services.insert(game_round=game_round_id,service=service,point_pool=point_pool)
	db.commit()
	return db.game_rounds[game_round_id]

def extract(d, keys):
	return dict((k, d[k]) for k in keys if k in d)

def get_team_role(user=None):
	if user is None: user = auth.user
	if user is None: return
	return db.team_users(user_id=user)

def get_owner_levels():   return ['owner']
def get_user_levels():    return ['owner','user']

def has_team_roles(roles, user=None):
	if user is None: user = auth.user
	if user is None: return
	query = db(db.team_users.user_id==user.id)
	query = query(db.team_users.role.belongs(roles))
	query = query(db.team_users.team==db.teams.id)
	return query.select(db.teams.ALL,limitby=(0,1)).first()

def require_team_roles(roles, user=None, error=404, **kwargs):
	team = has_team_roles(roles, user)
	if not team and error:
		if 'message' in kwargs: message = kwargs.pop('message')
		else: message = 'attempted to exceed authorization (%s)'%roles[-1]
		raiseUserError(error, message, **kwargs)
	return team

def is_team_owner(user=None): return has_team_roles(get_owner_levels(),user)
def is_team_user(user=None): return has_team_roles(get_user_levels(),user)

def require_team_owner(user=None, error=404, **kwargs): return require_team_roles(get_owner_levels(),user,error,**kwargs)
def require_team_user(user=None, error=404, **kwargs): return require_team_roles(get_user_levels(),user,error,**kwargs)

def get_team(user=None):
	team_user = get_team_role(user)
	if team_user is None: return
	return db.teams[team_user.team]

def get_team_owners(team):
	return db(db.team_users.team==team)(db.team_users.role=='owner')(db.team_users.user_id==db.auth_user.id).select(db.auth_user.ALL)

def get_user_public_keys(user=None):
	if user is None: user = auth.user
	if user is None: return logger.error('invalid user')
	entries = db(db.team_users.user_id==user.id)(db.team_users.public_key!=None).select(orderby=db.team_users.id)
	return [entry.public_key for entry in entries]

def get_team_public_keys(team):
	if team is None: return logUserError('invalid team')
	entries = db(db.team_users.team==team.id)(db.team_users.public_key!=None).select(orderby=db.team_users.id)
	return [entry.public_key for entry in entries]

def date_to_string(dateobj):
	return dateobj.strftime('%B %d, %Y at %I:%M %p (UTC)')

def userHasMembership(role,userID=None):
	if userID is None or (auth.user and userID == auth.user.id):
		if role == 'admin': return auth.has_membership(role='admin')
		if auth.has_membership(role='admin'): return True
		return auth.has_membership(role=role)
	query = db(db.auth_group.role==role)(db.auth_group.id==db.auth_membership.group_id)
	return query(db.auth_membership.user_id==userID).count()>0

def isAdmin(userID=None):
	return userHasMembership('admin',userID)

def getGameState():
	if request.utcnow < gameStartsAt(): return 'pre-game'
	if request.utcnow > gameEnds(): return 'post-game'
	return 'active'

def getGameStatusMessage():
	if request.utcnow < gameStartsAt():
		return 'Game starts %s'%date_to_string(gameStartsAt())
	if request.utcnow > gameEndsAt():
		return 'Game ended %s'%date_to_string(gameEndsAt())
	return 'Game is live!'.upper()

def idURL(id, *args, **kwargs):
	name = kwargs.pop('idvar','id')
	vargs = kwargs.get('vars',Storage())
	vargs[name] = id
	kwargs['vars'] = vargs
	return URL(*args, **kwargs)

class IS_PUBLIC_KEY(gluon.validators.Validator):
	# accepts RSA, DSA, ECDSA, and ED25519 (not RSA1)
	def __init__(self, types=None, error_message='Please enter a valid SSH public key'):
		self.error_message = error_message
		self.types = types

	def __call__(self, value):
		translate = gluon.validators.translate
		if value is None: return (value, translate(self.error_message))

		tokens = value.split(' ',2)
		if len(tokens) < 2: return (value, translate(self.error_message))
		type_headers = {'rsa':'ssh-rsa','dsa':'ssh-dss','ecdsa':'ecdsa-sha2-nistp256','ed25519':'ssh-ed25519'}
		if self.types: accepted_types = [type_headers[type] for type in self.types]
		else: accepted_types = type_headers.values()

		import base64, re
		header = tokens[0]
		b64data = tokens[1]
		if header not in accepted_types: return (value, translate(self.error_message))
		if not re.match('^[a-zA-Z0-9+/=]+$',b64data): return (value, translate(self.error_message))
		try:
			data = base64.b64decode(b64data)
		except:
			return (value, translate(self.error_message))
		return ('%s %s'%(header,b64data),None)
