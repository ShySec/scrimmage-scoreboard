def index():
	if auth.user:
		if isDebug() and str(request.env.REQUEST_URI).endswith('.jpg'): return dict()
		try:
			logUserError('error visiting %s://%s%s',request.env.UWSGI_SCHEME,request.env.HTTP_HOST,request.env.REQUEST_URI)
			if request.post_vars: logUserError('request.post_vars = %s',request.post_vars)
		except:
			logUserException('error (failed to get path)\n%s',request)
	return dict()
