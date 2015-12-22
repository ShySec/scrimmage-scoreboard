response.logo = A(B('SamuraiCTF'), _class="navbar-brand",_href="https://twitter.com/SamuraiCTF", _id="logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

response.meta.author = 'kelson <kelson@shysecurity.com>'
response.meta.description = 'Samurai CTF Scoreboard'
response.meta.keywords = 'samurai scoreboard'
response.meta.generator = ''

response.google_analytics_id = None

#########################################################################
response.menu = [
    #(T('Home'), False, URL('default', 'index'), []),
    (T('Graphics'), False, '/pretty'),
    (T('Teams'), False, '/teams'),
    (T('Services'), False, '/services'),
    (T('Rounds'), False, '/rounds'),
]

if auth.user:
	if is_team_owner(): response.menu.append((T('My Team'), False, '/team'))
	response.menu.append((T('Submit Flags'), False, '/flags'))

if auth.has_membership('admin'):
	response.menu.insert(2,(T('Servers'), False, '/servers'))

if "auth" in locals(): auth.wikimenu()

auth_dropdown = auth.navbar('Account',mode='dropdown')
if auth.user:
	auth_submenu = auth_dropdown.element('ul')
	auth_submenu.insert(1,LI(A(I(_class='icon icon-user glyphicon glyphicon-user'),'Team',_rel='nofollow',_href='/team')))
else:
	auth_submenu = auth_dropdown.element('ul')
	auth_submenu.insert(0,LI(A(I(_class='icon icon-off glyphicon glyphicon-off'),' Log In w/ GitHub',_rel='nofollow',_href='/github/login')))
	auth_submenu.insert(5,LI(A(I(_class='icon icon-user glyphicon glyphicon-user'),' Sign Up w/ GitHub',_rel='nofollow',_href='/github/register')))
