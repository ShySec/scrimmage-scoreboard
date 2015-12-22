def init_auth_user(db):
	#pwd = str(CRYPT()('pwd')[0])
	#db.auth_user.update_or_insert(dict(email='<email>'),first_name='<first>',last_name='<last>',email='<email>',password=pwd)
	db.commit()

def init_auth_group(db):
	db.auth_group.update_or_insert(dict(role='admin'), role='admin', description='Account Administrators')
	#admin = db(db.auth_user.email=='<email>').select().first()
	#for group in db(db.auth_group).select(): db.auth_membership.update_or_insert(user_id=admin,group_id=group)
	db.commit()

def init_teams(db):
	team = db.teams.insert(status='disabled',name='samurai')
	db.commit()

def init_services(db):
	text = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '

	# 10001 - eliza
	service = db.services.insert(status='active',port=10001,name='eliza',color='#957bb7')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='eliza/01_prompt.sh',name='e01-prompt')
	db.service_tests.insert(service=service, filename='eliza/02_help.sh',name='e02-help')
	db.service_tests.insert(service=service, filename='eliza/03_info_raw.sh',name='e03-info')
	db.service_tests.insert(service=service, filename='eliza/04_info_eliza.sh',name='e04-eliza')

	# 10002 - imapX
	service = db.services.insert(status='active',port=10002,name='imapX',color='#91ccd6')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='imapX/01_prompt.sh',name='i01-prompt')

	# 10003 - justify
	service = db.services.insert(status='active',port=10003,name='justify',color='#fe7518')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')

	# 10004 - wdub
	service = db.services.insert(status='active',port=10004,name='wdub',color='#996699')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')

	# 10005 - bash
	service = db.services.insert(status='active',port=10005,name='bash',color='#0099cc',token_letters=text,token_length=40)
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='bash/01_stateful_tmp.py',name='b01-stateful /tmp')
	db.service_tests.insert(service=service, filename='bash/02_chroot_check.sh',name='b02-chroot')
	db.service_tests.insert(service=service, filename='bash/03_echo.sh',name='b03-echo')

	# 10006 - exploitme
	service = db.services.insert(status='active',port=10006,name='exploitme',color='#cc9933')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='exploitme/01_empty.sh',name='e01-empty')

	# 10007 - patchme
	service = db.services.insert(status='active',port=10007,name='patchme',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='patchme/01_echo.sh',name='p01-echo')

	# 10008 - replayme
	service = db.services.insert(status='active',port=10008,name='replayme',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='replayme/01_echo.sh',name='r01-echo')
	db.service_tests.insert(service=service, filename='replayme/02_valid.sh',name='r02-valid')
	db.service_tests.insert(service=service, filename='replayme/03_invalid.sh',name='r03-invalid')

	# 10009 - babycmd
	service = db.services.insert(status='active',port=10009,name='babycmd',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')

	# 10010 - babyecho
	service = db.services.insert(status='active',port=10010,name='babyecho',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')

	# 10011 - r0pbaby
	service = db.services.insert(status='active',port=10011,name='r0pbaby',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')

	# 10012 - atmail
	service = db.services.insert(status='active',port=10012,name='atmail',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='atmail/01_availability.pl',name='a01-availability',timeout=20)

	# 10013 - avoir
	service = db.services.insert(status='active',port=10013,name='avoir',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='avoir/01_availability.py',name='a01-availability')

	# 10014 - bookworm
	service = db.services.insert(status='active',port=10014,name='bookworm',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='bookworm/01_availability.pl',name='b01-availability')

	# 10015 - lonetuna_v1
	service = db.services.insert(status='disabled',		port=10015,name='lonetuna_v1',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='lonetuna/01_availability.py',name='l01-availability')

	# 10016 - lonetuna_v2
	service = db.services.insert(status='disabled',		port=10016,name='lonetuna_v2',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='lonetuna/01_availability.py',name='l01-availability')

	# 10017 - reeses
	service = db.services.insert(status='active',port=10017,name='reeses',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='reeses/01_availability.py',name='r01-availability',timeout=10)

	# 10018 - trouver
	service = db.services.insert(status='active',port=10018,name='trouver',color='#006633')
	db.service_tests.insert(service=service, filename='tests/01_connectivity.sh',name='u01-connectivity')
	db.service_tests.insert(service=service, filename='trouver/01_availability.py',name='t01-availability')

	db.commit()
