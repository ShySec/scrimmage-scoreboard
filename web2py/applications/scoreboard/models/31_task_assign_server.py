def task_assign_server(team_id, host=None):
	logger.debug('assigning server to team %s',team_id)
	team = db.teams[team_id]
	if not team: return logger.error('failed to locate team')

	if host is None: host = team.host
	if host is None:
		server = db.team_server_pool(status='active',assigned=None)
		if not server: return emailUserError('no servers available')
		server.update_record(assigned=team)
		host = server.address
	logger.info('assigning team %s server %s',team.name,host)
	team.update_record(host=host,status='assigned')

	if task_set_team_credentials(team_id) and isGameActive():
		send_assignment(team=team)
	return True

def task_unassign_server(team_id=None):
	team=db.teams[team_id]
	if team is None: return logger.error('invalid team: %s',team_id)
	if team.host is None: return logger.error('missing team host: %s (%d)',team.name,team.id)

	pool_entry = db.team_server_pool(address=team.host)
	if pool_entry is not None:
		if not pool_entry.assigned:
			# log and continue (team access to server needs to be removed)
			logger.error('invalid entry assignment: %s',pool_entry.as_dict())
		elif pool_entry.assigned != team.id:
			return logger.error('server assigned to another team (%s vs %s)',team.name,pool_entry.assigned.name)
		pool_entry.update_record(assigned=None)

	return task_clear_team_credentials(team_id)

def task_set_team_credentials(team_id):
	team = db.teams[team_id]
	if not team: return logger.error('invalid team: %d',team_id)
	if not team.host: return logger.error('invalid team host: %s (%d)',team.name,team.id)

	public_keys = get_team_public_keys(team)
	if public_keys is None: return logger.error('invalid team public keys: %s (%d)',team.name,team.id)
	logger.debug('setting %d public keys for %s@%s',len(public_keys),team.name,team.host)
	if not task_transfer_public_keys(team.name,team.host,'\n'.join(public_keys)):
		logger.error('failed to transfer public keys for %s@%s',team.name,team.host)
		team.update_record(status='failed')
		return False
	team.update_record(status='active')
	return True

def task_clear_team_credentials(team_id):
	team = db.teams[team_id]
	if not team: return logger.error('invalid team: %d',team_id)
	if not team.host: return logger.error('invalid team host: %s (%d)',team.name,team.id)

	logger.debug('clearing public keys for %s@%s',team.name,team.host)
	if not task_transfer_public_keys(team.name,team.host,''):
		emailUserError('failed to clear public keys')
		return False
	team.update_record(status='inactive')
	return True

def task_transfer_public_keys(name, host, public_keys):
	import subprocess
	logger.debug('transfering keys for %s@%s',name,host)
	command = ['./transfer_public_key','ctf',host,name,public_keys]
	base_path = '/home/ctf/scoreboard'

	command = map(str,command)
	logger.debug('executing %s',command)
	try:
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=base_path)
		stdout,stderr = process.communicate()
		status = process.returncode
	except Exception as E:
		logger.exception('transfer failed! %s',command)
		emailUserError('transfer failed! %s',command)
		stdout,stderr = 0,0
		status = -1
	if status != 0:
		emailUserError('failed to transfer public keys for %s@%s',name,host)
		logger.error('transfer failed: %d',status)
		logger.error('stdout: %s',stdout[:2000])
		logger.error('stderr: %s',stderr[:2000])
		return False
	logger.debug('transferred keys for %s@%s',name,host)
	websocket_refresh()
	return True

def task_transfer_keys():
	for team in db(db.teams.host!=None)(db.teams.status!='disabled').select():
		task_set_team_credentials(team.id)
