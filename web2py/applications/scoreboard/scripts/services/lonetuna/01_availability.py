#!/usr/bin/env python
# https://github.com/legitbs/scorebot/blob/master/scripts/lonetuna/availability
import sys
import socket
import struct
import os
import random
import signal

def randstr( leng=6 ):
        x = ''
        for i in range(0, leng):
                x += struct.pack('B', random.randint( 0x41, 0x5b ))
        return x

def makefont( ):
	numglyphs = random.randint(0x10, 0x5e)
	print 'Num glyphs: %d' % numglyphs
	font = struct.pack('B', numglyphs&0xff)
	font += '\x69\x69\x69'
	for i in range(0, numglyphs):
		for x in range(0, 21):
			font += struct.pack('B', x)
		font += '\x00'
	font += '\x96\x96\x96'
	for i in range(0, 0x5e):
		font += struct.pack('B', random.randint(0, numglyphs-1))
	print len(font)
	print 'expexted: %d' % (7+(numglyphs*21)+0x5e + numglyphs)

	return font

def sender(s, data, display=True):
	s.send(data)
	print '>',data.rstrip('\n')

def recver(s, display=True):
	data = s.recv(4096)
	if display: print '>',data.rstrip('\n')
	return data

if __name__== '__main__':
  if len(sys.argv) < 3:
    print 'usage: %s <host> <port>'%sys.argv[0]
    sys.exit(1)

  host = sys.argv[1]
  port = int(sys.argv[2])

  signal.alarm( 10 )
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    s.connect((host,port))
  except socket.error, (value,message):
    sys.exit(1)

  data = recver(s)
  while not data.startswith('Connect'):
    data = recver(s)

  sfd = data[11:data.find(' to view')]
  recver(s)
  port = int(sfd)
  print 'Going to port: %d'% port
  try:
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect( (host, port ) )
  except socket.error, (value,message):
    print 'random port connect failed'
    sys.exit(1)

  print 'connected to %d' %port
  numfonts = random.randint( 1, 4 )
  for i in range(0, numfonts):
    sender(s,'2\n')
    font = makefont()
    sender(s,struct.pack('I', len(font)))
    sender(s,font)
    recver(s)
    sender(s,'1\n')
    sender(s,randstr(5) + '\n')
    recver(s)
    recver(c)

  sender(s,'3\n')
  y = recver(s)
  if not y.startswith('Thank you'):
	  print 'failed sla'
    sys.exit(1)
  s.close()
  print 'Successful sla'
