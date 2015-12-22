#!/usr/bin/env python2
import os
import sys
import logging
import requests
import collections
from pwn import *

SERVER=None
if SERVER is None:
	import socket
	SERVER='%s:8443'%(socket.gethostname())

def server_certificates():
	client = 'credentials.crt'
	if not os.path.exists(client): raise Exception('missing client credentials; re-run ./deploy')

	server = '../web2py/config/ssl/scoreboard.server.crt'
	if not os.path.exists(server): raise Exception('missing server credentials; re-run ./deploy')
	return dict(verify=server,cert=client)

def get_game_round():
	data=requests.get('https://%s/api/game_round'%SERVER,**server_certificates()).json()
	if 'error' in data: return logger.error('failed to get game round: %s',data['error'])
	return int(data['number'])

def get_teams(game_round):
	response=requests.get('https://%s/api/teams'%SERVER,dict(game_round=game_round,filtered=True),**server_certificates())
	return response.json()

def get_services(game_round):
	response=requests.get('https://%s/api/services'%SERVER,dict(game_round=game_round),**server_certificates())
	return response.json()

def report_tokens(tokens):
	response=requests.post('https://%s/flags/upload'%SERVER,json=tokens,**server_certificates())
	if response.status_code != 200: logger.error('upload failed %d: %s',response.status_code,response.text)
	logger.debug('upload succeeeded %d: %s',response.status_code,str(response.text)[:200])

def report_failures(failures):
	if not failures: return
	response=requests.post('https://%s/flags/failures'%SERVER,json=failures,**server_certificates())
	if response.status_code != 200: logger.error('uploading failures failed %d: %s',response.status_code,response.text)
	logger.debug('uploading failures succeeeded %d: %s',response.status_code,str(response.text)[:200])

def generate_token(length=40):
	import random, string
	return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(length))

def put_tokens(teams, services, keyfile, tokens, user='root'):
	logger.info('rotating %d teams and %d services',len(teams),len(services))
	if not len(services) or not len(teams): return
	mapping = collections.defaultdict(lambda:collections.defaultdict(str))
	for token in tokens: mapping[token['team']][token['service']]=token['token']

	failures = []
	for team in teams:
		team_tokens = mapping.get(team['name'],{})
		try:
			put_client_tokens(user, keyfile, team, services, team_tokens)
		except:
			logger.exception('failed to upload tokens to %s@%s',team['name'],team['host'])
			failures.extend([dict(token=token) for token in team_tokens.values()])
	logger.debug('rotation complete')
	return failures

def put_client_tokens(user, keyfile, team, services, mapping):
	client = ssh(user,team['host'],22,keyfile=keyfile)
	for service in services:
		token = mapping.get(service['name'])
		if not token:
			logger.error('failed to find token for %s:%s - abort!',team['name'],service['name'])
			continue
		put_token(client, service['name'], token)
		logger.debug('%s:%s => %s',team['name'],service['name'],token)
	if client: client.close()

def put_token(client, service, token):
	if not client: return
	client.shell('echo "%s" > /home/%s/flag'%(token,service))

def gen_tokens(teams, services, keyfile, user='root'):
	tokens=[]
	for team in teams:
		for service in services:
			token = generate_token()
			tokens.append(dict(team=team['name'],service=service['name'],token=token))
			logger.debug('%s:%s => %s',team['name'],service['name'],token)
	return tokens

if __name__ == '__main__':
	if len(sys.argv)<2:
		print 'usage: %s <keyfile>'%sys.argv[0]
		sys.exit(0)
	keyfile = sys.argv[1]
	logger = logging.getLogger()
	logformat = "%(asctime)s %(process)05d:%(levelname)5s %(funcName)s():%(lineno)d %(message)s"
	logging.basicConfig(level=logging.DEBUG,filename='logs/rotator.log',format=logformat)

	game_round = get_game_round()
	if not game_round: sys.exit(1)
	teams = get_teams(game_round)
	services = get_services(game_round)
	logging.debug('loaded %d teams and %d services on round %d',len(teams),len(services),game_round)
	tokens = gen_tokens(teams, services, keyfile)
	report_tokens(tokens)
	failures = put_tokens(teams, services, keyfile, tokens)
	report_failures(failures)
	logging.info('reporting %d updates',len(tokens))
