from sqlalchemy import *
import json

cfg = {}
user = None

def process(args, config, userdata):
	global cfg, user
	cfg = config
	user = userdata
	return {
		'show' : show,
	}.get(args[1], help)(args[:1] + args[2:])

def help(args):
	reply  = \
		'Available commands:\n' \
		'  show      shows all information about your account'
	return { 'status': 0, 'reply': reply }

def show(args):
	global cfg, user
	status = 0

	db = create_engine("%s://%s:%s@%s/%s" % (cfg['dbdrv'], cfg['dbuser'], cfg['dbpass'], cfg['dbaddr'], cfg['dbname']))
	raccount = db.execute("SELECT * FROM `accounts` WHERE uid=%s" % (user.pw_uid))
	rdata    = db.execute("SELECT * FROM `accounts_data` WHERE uid=%s" % (user.pw_uid))

	data = {}
	for row in raccount:
		data['login'] = row['login']
		data['uid']   = row['uid']
		data['gid']   = row['gid']
		data['shell'] = row['shell']
	
	for row in rdata:
		data['first_name'] = row['first_name']
		data['last_name']  = row['last_name']
		data['city']       = row['city']
		data['postcode']   = row['postcode']
	
	if args[0] == 'json':
		reply = json.dumps(data)
	else:
		reply = format_show(data)

	return { 'status': status, 'reply': reply }

def format_show(data):
	return \
		'Account information:\n' \
		+ '  Username:  %s\n'    %  data['login'] \
		+ '  UID:GID:   %s:%s\n' % (data['uid'], data['gid']) \
		+ '  Shell:     %s\n'    %  data['shell'] \
		+ '  Name:      %s %s\n' % (data['first_name'], data['last_name']) \
		+ '  City:      %s\n'    %  data['city'] \
		+ '  Post Code: %s\n'    %  data['postcode']

