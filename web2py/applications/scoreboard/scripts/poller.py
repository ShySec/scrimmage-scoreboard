#!/bin/env python
# crontab ~/scoreboard/settings/ctf_crontab
# python web2py.py -M -S scoreboard -R applications/scoreboard/scripts/poller.py -A DEBUG
import os
import sys
import time
import signal
import random
import logging
import threading
import subprocess

DEBUG=False
THREADING=False
TIMEOUT=2
VARIANCE=(1,120)
SERVICE_PATH='applications/scoreboard/scripts'

def random_delay():
	if not THREADING: return
	if DEBUG: return
	return time.sleep(random.randint(*VARIANCE))

def generate_token(service):
	return ''.join(random.choice(service['token_letters']) for x in range(service['token_length']))

class Alarm(Exception):
	pass

def alarm_handler(signum, frame):
	raise Alarm

def simulated_team_service_test(dbguard, game_round, service_test, team_service):
	if dbguard: dbguard.acquire()
	service_test_result = dict(game_round=game_round,service_test=service_test,team_service=team_service)
	service_test_result.update(status_code=0,stdout='',stderr='')
	db.team_service_test_results.insert(**service_test_result)
	if dbguard: dbguard.release()

def test_team_service(dbguard, game_round, service_test, team_service):
	if team_service.team.simulated_server:
		return simulated_team_service_test(dbguard, game_round, service_test, team_service)
	random_delay()
	if dbguard: dbguard.acquire()
	timeout = TIMEOUT

	try:
		service = service_test.service
		test_script = service_test.filename
		test_path = os.path.join(SERVICE_PATH,'services')
		command = [test_script,team_service.team.host,service.port]
		if service_test.timeout: timeout = service_test.timeout

		if service.token_length > 0:
			next_token = generate_token(service)
			prev_round = db.game_rounds[game_round.id-1]
			prev_entry = db.team_service_test_tokens(game_round=prev_round,service_test=service_test,team_service=team_service)
			prev_token = prev_entry.token if prev_entry else ''
			command.extend([next_token,prev_token])

			db.team_service_test_tokens.insert(game_round=game_round,service_test=service_test,team_service=team_service,token=next_token)
	except:
		logger.exception('failed setup')
		if dbguard: dbguard.release()
		return
	if dbguard: dbguard.release()

	status,stdout,stderr = execute_service_test(command, test_path, timeout)

	if dbguard: dbguard.acquire()
	try:
		service_test_result = dict(game_round=game_round,service_test=service_test,team_service=team_service)
		service_test_result.update(status_code=status,stdout=stdout,stderr=stderr)
		db.team_service_test_results.insert(**service_test_result)
	except:
		logger.exception('failed update')
	if dbguard: dbguard.release()

def execute_service_test(command, test_path, timeout):
	process = None
	command = map(str,command)
	logger.debug('executing %s %s',command[0],' '.join("'%s'"%c for c in command[1:]))
	try:
		signal.alarm(timeout)
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=test_path)
		stdout,stderr = process.communicate()
		status = process.returncode
	except Alarm:
		try:
			if process: process.kill()
		except:
			pass
		logger.error('process timed out: %s'%command)
		stderr = 'command timed out'
		stdout =  ''
		status = -1
	except Exception as E:
		logger.exception('failed with command: %s'%command)
		stderr = str(E)
		stdout = ''
		status = -1
	if status == 0:
		logger.debug('test passed')
	else:
		logger.debug('test failed: %d',status)
		logger.debug('stdout: %s',stdout[:2000])
		logger.debug('stderr: %s',stderr[:2000])
	return status,stdout,stderr

if __name__ == '__main__':
	if 'logger' not in globals():
		logger = logging.getLogger()
		logformat = "%(levelname)5s:%(module)15s.%(funcName)-20s:%(lineno)4d: %(message)s'"
		logging.basicConfig(level=logging.DEBUG,format=logformat)

	if len(sys.argv)==2: DEBUG = (sys.argv[1]=='DEBUG')
	if not DEBUG:
		if os.path.exists('.pause.services') or os.path.exists('.pause.services.poller'):
			logger.info('skipping poll due to .pause file')
			sys.exit(0)
	signal.signal(signal.SIGALRM, alarm_handler)

	threads = []
	dbguard = threading.Lock()
	game_round = get_game_round()
	if game_round is None:
		logger.info('skipping poll due to 0th round')
		sys.exit(1)
	if game_round.status not in ['active'] and not DEBUG:
		logger.debug('polling already complete for round %d (%s)',game_round.id,game_round.status)
		sys.exit(0)
	logger.debug('game round %d',game_round.id)
	game_round.update_record(status='polling'); db.commit()
	for service_test in db(db.game_round_services.game_round==game_round)(db.game_round_services.service==db.service_tests.service)(db.service_tests.status=='active').select(db.service_tests.ALL):
		for team_service in db(db.game_round_teams.game_round==game_round)(db.game_round_teams.team==db.team_services.team)(db.team_services.service==service_test.service).select(db.team_services.ALL):
			if DEBUG:
				test_team_service(dbguard, game_round,service_test,team_service)
				continue
			if THREADING: threads.append(threading.Thread(target=test_team_service,args=(dbguard,game_round,service_test,team_service)))
			else:         test_team_service(dbguard, game_round,service_test,team_service)

	for thread in threads: thread.start()
	for thread in threads: thread.join()
	game_round.update_record(status='polled'); db.commit()
	logger.info('polling complete for round %d',game_round.id)
