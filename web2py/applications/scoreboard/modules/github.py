import requests
import gluon.contrib.login_methods.oauth20_account as OAuth2

class GithubAccount(OAuth2.OAuthAccount):
	standard_auth_url = 'https://github.com/login/oauth/authorize'
	standard_token_url = 'https://github.com/login/oauth/access_token'
	def __init__(self, scope, redirect_url, client_id, client_secret, auth_url=None, token_url=None):
		if not auth_url: auth_url=GithubAccount.standard_auth_url
		if not token_url: token_url=GithubAccount.standard_token_url
		super(self.__class__,self).__init__(self,
		                client_id=client_id,client_secret=client_secret,
		                auth_url=auth_url,token_url=token_url,scope=scope)
		self.base_path = 'https://api.github.com'
		self.redirect_uri = redirect_url

	def __redirect_uri(self, next=''):
		"""
		Build the uri used by the authenticating server to redirect
		the client back to the page originating the auth request.
		Appends the _next action to the generated url so the flows continues.
		"""
		if next is None: next = ''
		uri = '%s%s'%(self.redirect_uri,next)
		return uri

	def get_raw(self, path):
		token = self.accessToken()
		if not token: return self.login_url(self.redirect_uri)
		headers = dict(Authorization='token %s'%token)
		response = requests.get('%s/%s'%(self.base_path,path.lstrip('/')),headers=headers)
		if response.status_code != 200: return logUserError('failed github request: %s\n%s',response.status_code,response.text)
		return response

	def get_json(self, path):
		response = self.get_raw(path)
		if not response: return
		return response.json()

	def get(self, path):
		return self.get_json(path)

	def get_user(self):
		return self.get('/user')

	def get_email(self):
		return self.get('/user/emails')

	def get_public_keys(self):
		return self.get('/user/keys')
