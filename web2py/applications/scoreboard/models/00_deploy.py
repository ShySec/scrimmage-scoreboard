from gluon.contrib.appconfig import AppConfig
myconf = AppConfig(reload=True) # private/appconfig.ini

def isDeployed():
	return myconf.take('env.debug',cast=int) != 1

def isDebug():
	if isDeployed(): return False
	return True

def gameStartsAt():
        return datetime.utcnow()+timedelta(days=1)

def gameEndsAt():
        return datetime.utcnow()+timedelta(days=2)

def GithubAPI(): # https://developer.github.com/v3/oauth/
	return dict(client_id='<github-client-id>',client_secret='<github-client-secret>')
