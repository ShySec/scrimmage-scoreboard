def extract_x509_credentials(request):
	import re
	if not request.is_https: return
	if not request.get('env',{}).get('ssl_client_raw_cert'): return
	try:
		import OpenSSL.crypto
		raw_cert = request.env.ssl_client_raw_cert
		der_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,raw_cert)
		components = dict(der_cert.get_subject().get_components())
	except:
		return logUserException('x509 certificate extraction failed')
	team = components.get('OU')
	email = components.get('CN')
	if not team or not email: return logUserError('invalid certificate subject: %s',str(components))
	return dict(team=team,email=email)

def in_str_or_list(haystack, needle):
	if type(haystack) == str:
		return needle == haystack
	if type(haystack) in [tuple,list,set]:
		return needle in haystack
	return False

def requires_x509_certificate_decorator(request, require_team=None, require_email=None, *args, **kwargs):
	credentials = extract_x509_credentials(request)
	if not credentials: raise HTTP(403,'Not authorized')
	team_name,user_email = credentials['team'],credentials['email']
	if require_email and not in_str_or_list(require_email,user_email):
		logUserError('unauthorized email: %s [%s] (team %s)',user_email,require_email,team_name)
		raise HTTP(403,'Not authorized')
	if require_team and not in_str_or_list(require_team,team_name):
		logUserError('unauthorized team: %s [%s] (team %s)',team_name,require_team,user_email)
		raise HTTP(403,'Not authorized')
	return (team_name,user_email)

def requires_x509_certificate(self, require_team=None, require_email=None):
	"""
	Decorator that prevents access to action if client certificate not provided.
	"""
	def decorator(action):
		def x509_certificate(*args, **kwargs):
			_=requires_x509_certificate_decorator(request, require_team, require_email, *args, **kwargs)
			return action(*args, **kwargs)
		x509_certificate.__doc__ = action.__doc__
		x509_certificate.__name__ = action.__name__
		x509_certificate.__dict__.update(action.__dict__)
		return x509_certificate
	return decorator

auth.requires_x509_certificate = requires_x509_certificate.__get__(auth,Auth)

def requires_x509_login_decorator(request, require_team=None, require_email=None, *args, **kwargs):
	team_name,user_email=requires_x509_certificate_decorator(request, require_team, require_email, *args, **kwargs)
	team = db.teams(name=team_name)
	if not team:
		logUserError('invalid team name: %s (user = %s)',team_name,user_email)
		raise HTTP(403,'Not authorized')
	user = db.auth_user(email=user_email)
	if not user:
		logUserError('invalid user email: %s (team = %s)',user_email,team_name)
		raise HTTP(403,'Not authorized')
	if not db.team_users(team=team,user_id=user):
		logUserError('invalid user/team combo: %s (team = %s)',user_email,team_name)
		raise HTTP(403,'Not authorized')
	auth.login_user(user)
	return (team,user)

def requires_x509_login(self, require_team=None, require_email=None):
	"""
	Decorator that prevents access to action if client certificate doesn't match valid user/team.
	"""
	def decorator(action):
		def x509_login(*args, **kwargs):
			team,user=requires_x509_login_decorator(request, require_team, require_email, *args, **kwargs)
			return action(*args, **kwargs)
		x509_login.__doc__ = action.__doc__
		x509_login.__name__ = action.__name__
		x509_login.__dict__.update(action.__dict__)
		return x509_login
	return decorator

auth.requires_x509_login = requires_x509_login.__get__(auth,Auth)
