#!/usr/bin/env python2
import sys
import socket

def connect(host, port):
	s = socket.socket()
	s.connect((host,port))
	return s

def parse_token(token):
	if not token: return token
	return dict(path='%s'%token[:20],data='%s'%token[20:])

def get(host, port, token):
	s = connect(host,port)
	s.send("exec cat '/tmp/%s'\r\n"%token['path'])
	data = s.recv(4096)
	s.close()
	return data

def put(host, port, token):
	s = connect(host,port)
	s.send("echo -n '%s' > '/tmp/%s'\r\n"%(token['data'],token['path']))
	s.close()

if __name__ == '__main__':
	if len(sys.argv) != 5:
		print 'usage: %s <host> <port> <next_token> <prev_token>'%sys.argv[0]
		sys.exit(1)
	host,port,next_token,prev_token = sys.argv[1:]
	next_token = parse_token(next_token)
	prev_token = parse_token(prev_token)

	port = int(port)
	if prev_token: test_data = get(host,port,prev_token)
	put(host,port,next_token)

	if prev_token and prev_token['data'] != test_data:
		sys.stdout.write(test_data)
		sys.stdout.flush()
		message = 'previous token mismatch: expected "%s"\n'%(prev_token['data'])
		sys.stderr.write(message)
		sys.stderr.flush()
		sys.exit(2)
