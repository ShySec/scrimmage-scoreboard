#!/bin/env python
# python web2py.py -M -S scoreboard -R applications/scoreboard/scripts/setup.py
import os
import sys

def initialize_databases():
	if db(db.auth_user).count() < 1:
		import db_initialize
		db_initialize.init_auth_user(db)

	if db(db.auth_group).count() < 1:
		import db_initialize
		db_initialize.init_auth_group(db)

	if db(db.services).count() < 1:
		import db_initialize
		db_initialize.init_services(db)

	if db(db.teams).count() < 1:
		import db_initialize
		db_initialize.init_teams(db)

if __name__ == '__main__':
	import getpass
	email = os.environ.get('SCOREBOARD_EMAIL')
	password = os.environ.get('SCOREBOARD_CRYPT')
	if not email: raw_input('Email: ').strip()
	while not password:
		interactive_password = getpass.getpass('Password: ')
		interactive_confirm = getpass.getpass('Confirm: ')
		if interactive_password != interactive_confirm: continue
		password = str(CRYPT()(interactive_password)[0])
	if db.auth_user(email=email):
		print 'user already registered: aborting setup'
		sys.exit(0)
	initialize_databases()
	user = db.auth_user.insert(email=email,password=password)
	db.auth_membership.insert(user_id=user,group_id=db.auth_group(role='admin'))
	db.commit()
	print 'added admin "%s"'%email
