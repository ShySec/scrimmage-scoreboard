@auth.requires_membership('admin')
def index():
	host_validators = [IS_IPV4(error_message='please enter a valid IPv4 address in dotted decimal form', is_localhost=False, is_private=False, is_automatic=False),
	                   IS_NOT_IN_DB(db,db.teams.host,'server address already in use')]

	table = TABLE(TR(INPUT(_type='submit', _value='Add Server',_class='btn btn-success'),
	                 INPUT(_name='host',   _class='server',    requires=host_validators, _placeholder='add a new IPv4 address to the server pool'),
	              ))
	form = FORM(table)
	if form.validate():
		address = form.vars.host.strip()
		logUserDebug('registering server %s',address)
		db.team_server_pool.insert(contributor=auth.user,status='active',address=address)
		response.flash='Server registered'

	teams = db(db.teams).select(orderby=db.teams.name)
	return dict(form=form,teams=teams)

@auth.requires_membership('admin')
def enable():
	server = lookupVarID('id',db.team_server_pool)
	if not server: raiseUserError(400,'enabling invalid server: %s',request.vars)
	if server.assigned: raiseUserError(400,'enabling assigned server %d',server.id)
	if server.status == 'active':
		logUserDebug('re-enabling active server %d',server.id)
	else:
		logUserDebug('enabling server %d',server.id)
		server.update_record(status='active')
	return ''

@auth.requires_membership('admin')
def disable():
	server = lookupVarID('id',db.team_server_pool)
	if not server: raiseUserError(400,'disabling invalid server: %s',request.vars)
	if server.assigned: raiseUserError(400,'disabling assigned server %d',server.id)
	if server.status == 'disabled':
		logUserDebug('re-disabling disabled server %d',server.id)
	else:
		logUserDebug('disabling server %d',server.id)
		server.update_record(status='disabled')
	return ''

@auth.requires_membership('admin')
def delete():
	server = lookupVarID('id',db.team_server_pool)
	if not server: raiseUserError(400,'deleting invalid server: %s',request.vars)
	if server.assigned: raiseUserError(400,'deleting assigned server %d',server.id)
	if server.status == 'active': raiseUserError(400,'deleting active server %d',server.id)
	logUserDebug('deleting server %d',server.id)
	server.delete_record()
	return ''

@auth.requires_membership('admin')
def assign():
	team = lookupVarID('team',db.teams)
	server = lookupVarID('id',db.team_server_pool)
	if not team: raiseUserError(400,'accessing invalid team: %s',request.vars)
	if not server: raiseUserError(400,'accessing invalid server: %s',request.vars)
	if server.assigned: raiseUserError(400,'re-assigning assigned server %d to %d',server.id,team.id)
	if server.status != 'active': raiseUserError(400,'assigning disabled server %d to %d',server.id,team.id)
	logUserDebug('assigning server %d to team %d',server.id,team.id)
	for prior in db(db.team_server_pool.assigned==team.id).select():
		logUserDebug('deassigning server %d (team %d)',prior.id,team.id)
		prior.update_record(assigned=None)
	if team.status == 'inactive': team.update_record(status='active')
	team.update_record(host=server.address)
	server.update_record(assigned=team)
	return ''

@auth.requires_membership('admin')
def unassign():
	server = lookupVarID('id',db.team_server_pool)
	if not server: raiseUserError(400,'accessing invalid server: %s',request.vars)
	if not server.assigned: raiseUserError(400,'unassigning unassigned server %d',server.id)
	team = db.teams[server.assigned]
	logUserDebug('unassigning server %d (team %d)',server.id,team.id)
	if team.status != 'disabled': team.update_record(status='inactive')
	server.update_record(assigned=None)
	team.update_record(host=None)
	return ''
