#!/usr/bin/env python
# https://github.com/legitbs/scorebot/blob/master/scripts/trouver/availability

import random
import socket
import sys
import struct
import signal

def sender(s, data, display=True):
	s.send(data)
	print '<',data.rstrip('\n')

def recver(s, display=True):
	data = s.recv(4096)
	if display: print '>',data.rstrip('\n')
	return data

def randstr( leng=6 ):
        x = ''
        for i in range(0, leng):
                x += struct.pack('B', random.randint( 0x41, 0x5b ))
        return x

def login(s):
	users = [ ['root', 'd41d8cd98f00b204e9800998ecf8427e'], ['c0mrade', '48bb6e862e54f2a795ffc4e541caed4d'], ['mitnick', '0625c3fc57758122569f6695af3579a1'], ['gonzalez', 'e8008e06909d08bccc344f7e56b1461b'], ['poulsen', '41d0e299ca1abeb2094852da042165c7'], [ 'solo', '28ca53d2b7bb4aa13549b4022c79dca1']]
	x = random.randint(0, len(users)-1)
	fuck = users[x]
	sender(s,'PERS')
	sender(s,struct.pack('B', len(fuck[0])))
	sender(s,fuck[0])
	y = recver(s)
	if y.startswith('Yay for you') == False:
		print y
		print 'unexpected yay for you'
		return 1
	sender(s,'MOTS')
	sender(s,struct.pack('B', len(fuck[1])))
	sender(s,fuck[1])
	y = recver(s)
	if y.startswith('Thanks for all the ') == False:
		print 'unexpected thanks for all'
		return 1
	sender(s,'AUTH')
	y = recver(s)
	if y.startswith('Auth successful') == False:
		print 'auth not succ'
		return 1
	return 0

def sendget( s ):
	q = randstr( )
	data = randstr( random.randint(0x80, 0x100))
	sender(s,'DNNR')
	sender(s,struct.pack('H', len(q)))
	sender(s,q)
	sender(s, struct.pack('H', len(data)))
	sender(s,data)
	y = recver(s)
	if y.startswith('OOOh, good') == False:
		print y
		print 'unexpected response sendget'
		return 1
	sender(s,'PRND')
	sender(s,struct.pack('H', len(q)))
	sender(s,q)
	y = recver(s)
	z = recver(s)
	if y != data:
		print 'not same data'
		return 1
	if z.startswith('Yay for you') == False:
		print 'unexpected response yay for you'
		return 1
	return 0

def mdircd( s ):
	x = randstr( random.randint(10,15))
	sender(s,'FAIT')
	sender(s,struct.pack('H', len(x)))
	sender(s, x )
	y = recver(s)
	if y.startswith('Your wish') == False:
		print 'not what expected'
		return 1
	sender(s,'EVOL')
	sender(s,struct.pack('H', len(x)))
	sender(s,x)
	y = recver(s)
	if y.startswith('Done for you') == False:
		print 'EVOL failed'
		return 1
	sender(s,'ANNU')
	y = recver(s)
	if y.startswith('/' + x) == False:
		print 'annu failed'
		return 1
	return 0

def listdir( s ):
	x = randstr( random.randint(10,15))
	sender(s,'FAIT')
	sender(s,struct.pack('H', len(x)))
	sender(s, x)
	y = recver(s)
	if y.startswith('Your wish') == False:
		return 1
	sender(s,'NMMR')
	sender(s,struct.pack('H', 0x01))
	sender(s,'/')
	y = recver(s)
	if y.find(x) == -1:
		print 'NMMR failed'
		return 1
	return 0

def sendgetsize( s ):
	q = randstr( )
	data = randstr( random.randint(0x80, 0x300))
	sender(s,'DNNR')
	sender(s,struct.pack('H', len(q)))
	sender(s,q)
	sender(s, struct.pack('H', len(data)))
	sender(s,data)
	y = recver(s)
	if y.startswith('OOOh, good') == False:
		print 'DNNR failed'
		return 1
	sender(s,'POID')
	sender(s,struct.pack('H', len(q)))
	sender(s,q)
	y = recver(s)
	if int(y) != len(data):
		print 'unexpected data len'
		return 1

	return 0

def cmdloop( s ):
	retval = 0
	x = random.randint( 0, 3 )

	if x == 0:
		retval = sendget( s )
		if retval != 0:
			print 'sendget failed'
	if x == 1:
		retval = mdircd( s )
		if retval != 0:
			print 'mdircd failed'
	if x == 2:
		retval = sendgetsize( s )
		if retval != 0:
			print 'sendgetsize failed'
	if x == 3:
		retval = listdir( s )
		if retval != 0:
			print 'listdir failed'

	print retval
	sys.exit(retval)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print 'usage: %s <host> <port>'%sys.argv[0]
		sys.exit(1)

	host = sys.argv[1]
	port = int(sys.argv[2])

	signal.alarm(10)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
	except:
		print "connect failed"
		sys.exit(1)

	print recver(s)
	if login( s ) != 0:
		print 'login failed'
		sys.exit(1)
	else:
		print 'login success'

	cmdloop( s )
