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
	sites = args[1:]
	ret = []

	for s in sites:
		src = os.path.join(cfg['nginx:sites_available'], user.pw_name, s)
		dst = os.path.join(cfg['nginx:sites_enabled'], user.pw_name, s)

		if os.path.isfile(src):
			if os.path.exists(dst):
				ret.append({'message': 'Site %s is already enabled' % s})
			else:
				os.symlink(src, dst)
				devnull = open('/dev/null', 'w')
				subprocess.call(cfg['nginx:reload_cmd'].split(' '), stdout=devnull)
				ret.append({'message': 'Site %s enabled' % s})
		else:
			ret.append({'message': 'No site called %s' % s})
	return json.dumps(ret)

def site_disable(args):
	sites = args[1:]
	ret = []

	for s in sites:
		dst = os.path.join(cfg['nginx:sites_enabled'], user.pw_name, s)
		if os.path.exists(dst):
			os.unlink(dst)
			devnull = open('/dev/null', 'w')
			subprocess.call(cfg['nginx:reload_cmd'].split(' '), stdout=devnull)
			ret.append({ 'message': 'Site %s disabled' % s})
		else:
			ret.append({'message': 'Site %s is already disabled' % s})
	return json.dumps(ret)

def list_sites(args):
	data = []

	saval = os.listdir(os.path.join(cfg['nginx:sites_available'], user.pw_name))

	for s in saval:
		status = os.path.isfile(os.path.join(cfg['nginx:sites_enabled'], user.pw_name, s))
		data.append({
			'domain' : s,
			'status' : status,
		})
	
	# reverse order for sorting
	for d in data:
		d['domain'] = d['domain'].split('.')
		d['domain'].reverse()
	
	data = sorted(data, key=lambda k: k['domain'])

	# reverse again to show correct domain names
	for d in data:
		d['domain'].reverse()
		d['domain'] = '.'.join(d['domain'])

	if args[0] == 'json':
		return json.dumps(data)
	else:
		return format_list_sites(data)

def format_list_sites(data):
	ret = 'Your sites:\n\n'
 
 	counter = 0
	
	lennum  = len(data) / 10 + 1
	lenname = 1
	for site in data:
		if lenname < len(site['domain']):
			lenname = len(site['domain'])

	for site in data:
		counter += 1
		num  = ('{0: >#%s}' % lennum).format(counter)
		name = ('{0: >%s}' % lenname).format(site['domain'])
		if site['status'] == True:
			ret += '  %s  \033[1;32mon\033[0m   %s\n' % (num, name)
		else:
			ret += '  %s  \033[1;31moff\033[0m  %s\n' % (num, name)
	return ret
