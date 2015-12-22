#!/usr/bin/env python2
# https://github.com/legitbs/scorebot/blob/master/scripts/avoir/availability
import sys
import signal
import argparse
import socket
import select
import string
import io
import struct
import string
import random
import time
import hashlib

def randstr( leng=6 ):
	x = ''
	for i in range(0, leng):
		x += struct.pack('B', random.randint( 0x41, 0x5b ))
	return x

user = None

def recvtil( s, needle, display=True ):
	haystack = ''
	while True:
		data = s.recv(1024)
		if display: print data
		haystack += data
		if needle in haystack:
			return haystack

def sender( s, data ):
	s.send(data)
	print '>',data.rstrip('\n')

def catchup( s, display=False, strip=True ):
	s.send('ls /\n')
	token = '? No permissions to read: /'
	data = recvtil(s,token,display)
	data = data.rsplit(token,1)[0]
	return data.lstrip('? ')

def login( s ):
	users = [ [ 'billy\n', 'pilgrim\n'], [ 'kilgore\n', 'trout\n'], [ 'littlenewt\n', 'ice\n'], [ 'blackbeard\n', 'pirate\n'] ]

	global user
	user = random.choice(users)
	print user[0]
	y = s.recv(1024)
	if y.startswith('\nuser:') != True:
		print "user failed %s" % y
		return -1

	sender(s, user[0] )
	y = s.recv(1024)
	if y.startswith('pass:') != True:
		return -1

	sender(s,user[1])
	y = s.recv( 1024 )
	if y.startswith('login failed') == True:
		return -1
	return 0

def createdirls( s ):
	x = randstr( random.randint(0x10, 0x30) )
	sender(s,'md ' + x + '\n')
	sender(s,'ls .\n')
	y = catchup(s)
	if y.find(x) == -1:
		print "createdirls failed"
		return -1
	print 'createdirls success'
	return 0

def mkdirlsrmdir( s ):
	x = randstr( random.randint(0x10,0x30) )
	sender(s,'md ' + x + '\n')
	sender(s, 'ls .\n')
	y = catchup(s)
	if y.find(x) == -1:
		print y
		print x
		print 'mkdirlsrmdir failed'
		return -1
	sender(s,'rd ' + x + '\n')
	#print s.recv(1024)
	print 'mkdirlsrmdir success'
	return 0

def touchls( s ):
	x = randstr( random.randint(0x10,0x30) )
	sender(s,'th ' + x + '\n')
	sender(s, 'ls .\n')
	y = catchup(s)
	if y.find(x) == -1:
		print 'touchls failed'
		return -1
	print 'touchls success'
	return 0

def echocat( s ):
	x = randstr( random.randint( 0x10, 0xf0) )
	y = randstr( random.randint(0x10, 0x30) )
	blah = 'ec ' + x + ' >> ' + y + '\n'
	sender(s,blah)
	z = catchup(s)
	sender(s,'ct ' + y + '\n')
	z = catchup(s)
	if z != x:
		print z
		print x
		print 'echo cat failed'
		return -1
	print 'echo cat success'
	return 0

def addusersu( s ):
	x = randstr()
	sender(s,'au ' + x + '\n')
	passd = randstr()
	sender(s, passd + '\n')
	sender(s, passd + '\n')
	sender(s,'su ' + x + '\n')
	sender(s,passd + '\n')
	y = catchup(s)
	sender(s,'wh\n')
	y = catchup(s)
	if y.startswith(x) == False:
		print y
		print 'wh adduser failed'
		return -1
	sender(s, 'cd \n')
	y = catchup(s)
	sender(s, 'pd\n')
	y = catchup(s)
	z = '/home/' + x
	if y.startswith(z) == False:
		print y
		print 'pd adduser failed'
		return -1
	print 'addusersu success'
	#s.recv(1024)
	return 0

def runcmd( s ):
	sender(s,'cd /home/%s\n'%user[0])

	retval = 0
	x = random.randint( 0, 4 )
	if x == 0:
		retval = createdirls( s )
		if retval != 0:
			print 'createdirls failed'
	elif x == 1:
		retval = mkdirlsrmdir( s )
		if retval != 0:
			print 'mkdirlsrmdir failed'
	elif x == 2:
		retval = echocat( s )
		if retval != 0:
			print 'echocat failed'
	elif x == 3:
		retval = touchls( s )
		if retval != 0:
			print 'toucls failed'
	elif x == 4:
		retval = addusersu( s )
		if retval != 0:
			print 'addusersu failed'
	sys.exit(retval)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print 'usage: %s <host> <port>'%sys.argv[0]
		sys.exit(1)

	host = sys.argv[1]
	port = int(sys.argv[2])

	signal.alarm(10)
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
	s.connect(( host, port ) )

	print s.recv(1024)
	if login( s ) != 0:
		print 'Login failed'
		sys.exit(1)
	print 'login success'
	runcmd( s )
