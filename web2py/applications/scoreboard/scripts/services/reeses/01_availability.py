#!/usr/bin/python
# https://github.com/legitbs/scorebot/blob/master/scripts/reeses/availability
import os
import sys
import random
import signal

import sla_conf

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print 'usage: %s <host> <port>'%sys.argv[0]
		sys.exit(1)

	host = sys.argv[1]
	port = int(sys.argv[2])

	cwd = os.getcwd()
	os.chdir('reeses')
	signal.alarm(sla_conf.timeout)
	random.seed()
	func = sla_conf.slaList[random.randint(0,len(sla_conf.slaList)-1)]
	print func
	func( host, port )
	os.chdir(cwd)
