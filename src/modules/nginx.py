import json, os, subprocess

cfg = {}
user = None

def process(args, config, userdata):
	global cfg, user
	cfg = config
	user = userdata
	return {
		'enable'  : site_enable,
		'disable' : site_disable,
		'list'    : list_sites,
	}.get(args[1], help)(args[:1] + args[2:])

def help(args):
	return \
		'Available commands:\n\n' \
		'  enable <domain>     enables site\n' \
		'  disable <domain>    disables site\n' \
		'  list                list all sites with availability status\n'

def site_enable(args):
	src = os.path.join(cfg['nginx:sites_available'], user.pw_name, args[1])
	dst = os.path.join(cfg['nginx:sites_enabled'], user.pw_name, args[1])

	if os.path.isfile(src):
		if os.path.exists(dst):
			return json.dumps({ 'message': 'Site %s is already enabled' % args[1] })
		else:
			os.symlink(src, dst)
			devnull = open('/dev/null', 'w')
			subprocess.call(cfg['nginx:reload_cmd'].split(' '), stdout=devnull)
			return json.dumps({ 'message': 'Site %s enabled' % args[1] })
	else:
		return json.dumps({ 'message': 'No site called %s' % args[1]})

def site_disable(args):
	dst = os.path.join(cfg['nginx:sites_enabled'], user.pw_name, args[1])

	if os.path.exists(dst):
		os.unlink(dst)
		devnull = open('/dev/null', 'w')
		subprocess.call(cfg['nginx:reload_cmd'].split(' '), stdout=devnull)
		return json.dumps({ 'message': 'Site %s disabled' % args[1]})
	else:
		return json.dumps({ 'message': 'Site %s is already disabled' % args[1]})

def list_sites(args):
	data = {}

	saval = os.listdir(os.path.join(cfg['nginx:sites_available'], user.pw_name))
	for s in saval:
		status = os.path.isfile(os.path.join(cfg['nginx:sites_enabled'], user.pw_name, s))
		data[s] = status

	if args[0] == 'json':
		return json.dumps(data)
	else:
		return format_list_sites(data)

def format_list_sites(data):
	ret = 'Your sites:\n\n'

	for site,status in data.iteritems():
		if status == True:
			ret += '  \033[1;32mon\033[0m   %s\n' % site
		else:
			ret += '  \033[1;31moff\033[0m  %s\n' % site
	return ret
