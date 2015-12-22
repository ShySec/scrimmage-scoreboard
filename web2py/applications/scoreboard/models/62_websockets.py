def websocket_server():
	return myconf.take('websockets.server')

def websocket_send(data, group='viz', key=None):
	import json
	if not key: key=''
	from gluon.contrib.websocket_messaging import websocket_send
	try:
		return websocket_send(websocket_server(), json.dumps(data), key, group)
	except IOError:
		logger.error('failed to connect to websocket server')
	except:
		logger.exception('failed to update websocket server')

def websocket_pwn(src, dst, service):
	websocket_send({'type':'pwn', 'from':src['name'], 'to':dst['name'], 'service':service['name'], 'servicergb':service['color']})

def websocket_fail(team):
	websocket_send({'type':'fail', 'team':team['name']})

def websocket_pass(team):
	websocket_send({'type':'pass', 'team':team['name']})

def websocket_refresh():
	websocket_send({'type':'refresh'})
