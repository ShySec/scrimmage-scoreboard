grid_kwargs = dict(csv=False, create=False, deletable=False, editable=False, searchable=False, details=False)

@auth.requires_login()
def index():
	team = require_team_owner()

	profile = TABLE()
	profile.append(TR(LABEL('Team'),DIV(team.name,_class='col-sm-9')))
	profile.append(TR(LABEL('Secret'),DIV(team.secret,_class='col-sm-9')))
	profile.append(TR(LABEL('Server'),DIV(team.host,_class='col-sm-9')))
	profile.append(TR(LABEL('Status'),DIV(team.status,_class='col-sm-9')))

	fields = [db.auth_user.email]
	headers = {'auth_user.email':'Login'}
	query = (team.id==db.team_users.team)&(db.team_users.user_id==db.auth_user.id)
	links = [dict(header='',body=lambda row:A(BUTTON('Remove'),_href=URL('remove',vars=dict(id=row.id))))]
	users = SQLFORM.grid(query=query,fields=fields,links=links,orderby=db.auth_user.email, **grid_kwargs)

	return dict(profile=profile, users=users)

@auth.requires_login()
def remove_user():
	team = require_team_owner()

	target = lookupVarID('id',db.auth_user,error=404)
	team_user = get_team_role(target)
	if team_user is None: raiseUserError(403, 'attempted to remove invalid user %s',target)
	if team_user.team != team: raiseUserError(403, 'attempted to remove unaffiliated user')

	team_user.delete_record()
	logUserInfo('removed team mate %s',target.email)
	redirect(URL('team','index'))
