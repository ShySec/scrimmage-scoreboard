from gluon.tools import Auth, Crud, Recaptcha, Service, PluginManager, prettydate
# request.requires_https()

db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['sqlite','postgres'])

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

#########################################################################
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## add extra auth tables
auth.settings.extra_fields['auth_user'] = [
	Field('oauth_name', 'string', readable=False, writable=False),
	auth.signature
]
auth.settings.extra_fields['auth_group'] = [ auth.signature ]
auth.settings.extra_fields['auth_membership'] = [ auth.signature ]
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## record db structure
'''
auth.signature = [
          Field('is_active',          'boolean'),
          Field('created_on',         'datetime'),
          Field('created_by',         'reference auth_user'),
          Field('modified_on',        'datetime'),
          Field('modified_by',        'reference auth_user')
]

db.define_table('auth_user',
          Field('first_name',         'string'),
          Field('last_name',          'string'),
          Field('email',              'string'),
          Field('password',           'string'),
          Field('registration_key',   'string'),
          Field('reset_password_key', 'string'),
          Field('registration_id',    'string'),

          # custom additions
          Field('oauth_name', 'string', readable=False, writable=False),
          auth.signature)

db.define_table('auth_group'
          Field('role',               'string'),
          Field('description',        'string'),
          auth.signature)

db.define_table('auth_membership',
          Field('user_id',            'reference auth_user'),
          Field('group_id',           'reference auth_group'),
          auth.signature)

db.define_table('auth_permission',
          Field('group_id',           'reference auth_group'),
          Field('name',               'string'),
          Field('table_name',         'string'),
          Field('record_id',          'integer'),
          auth.signature)

db.define_table('auth_event',
          Field('time_stamp',         'datetime'),
          Field('client_ip',          'string'),
          Field('user_id',            'reference auth_user'),
          Field('origin',             'string'),
          Field('description',        'string'),
          auth.signature)

db.define_table('auth_cas',
          Field('user_id',            'reference auth_user'),
          Field('created_on',         'datetime'),
          Field('service',            'string'),
          Field('ticket',             'string'),
          Field('renew'               'string'),
          auth.signature)
'''
