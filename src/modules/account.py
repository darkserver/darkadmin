from sqlalchemy import *
import pwd, grp, time, json

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
	return \
		'Available commands:\n\n' \
		'  show      shows all information about your account\n'

def show(args):
	global cfg, user
	status = 0

	db = create_engine('%s://%s:%s@%s/%s' % (cfg['dbdrv'], cfg['dbuser'], cfg['dbpass'], cfg['dbaddr'], cfg['dbname']))
	rdata    = db.execute('SELECT * FROM `accounts_data` WHERE uid=%s' % (user.pw_uid))

	data = {
		'login'      : user.pw_name,
		'uid'        : user.pw_uid,
		'shell'      : user.pw_shell,
		'home'       : user.pw_dir,
		'groups'     : [],
		'first_name' : '',
		'last_name'  : '',
		'city'       : '',
		'phone'      : '',
		'postcode'   : '',
		'address'    : '',
		'valid'      : None,
	}

	for g in grp.getgrall():
		for u in g.gr_mem:
			if u == user.pw_name:
				data['groups'].append(g.gr_name)
	
	for row in rdata:
		data['first_name'] = row['first_name']
		data['last_name']  = row['last_name']
		data['city']       = row['city']
		data['postcode']   = row['postcode']
		data['address']    = row['address']
		data['phone']      = row['phone']
		if row['valid']:
			data['valid']  = str(row['valid'])
	
	if args[0] == 'json':
		return json.dumps(data)
	else:
		return format_show(data)

def format_show(data):
	if data['valid']:
		t = time.strftime('%d %B %Y', time.strptime(data['valid'], '%Y-%m-%d'))
	else:
		t = 'unlimited'
	return \
	    'Account information for user \033[1;36m%s\033[0m:\n\n' % data['login'] \
	  + '  \033[1;37mValid until:\033[0m %s\n'    %  t \
	  + '  \033[1;37mGroups:\033[0m      %s\n'    %  ' '.join(data['groups']) \
	  + '  \033[1;37mShell:\033[0m       %s\n'    %  data['shell'] \
	  + '  \033[1;37mName:\033[0m        %s %s\n' % (data['first_name'], data['last_name']) \
	  + '  \033[1;37mPhone:\033[0m       %s\n'    %  data['phone'] \
	  + '  \033[1;37mPost code:\033[0m   %s\n'    %  data['postcode'] \
	  + '  \033[1;37mAddress:\033[0m     %s\n'    %  data['city'] \
	  + '               %s\n'                     %  data['address']

