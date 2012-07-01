import json, os, subprocess, re
from log import *

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
		'add'     : site_add,
		'del'     : site_remove,
	}.get(args[1], help)(args[:1] + args[2:])

def help(args):
	return \
		'Available commands:\n\n' \
		'  list                   list all sites with availability status\n' \
		'  enable <domain>        enables site\n' \
		'  disable <domain>       disables site\n' \
		'  add <type> <domain>    adds site with type where type can be: php, django\n' \
		'  del <domain>           deletes site information, doesn\'t delete files\n'

def site_enable(args):
	sites = args[1:]
	reload_nginx = False
	ret = []

	for s in sites:
		src = os.path.join(cfg['nginx:sites_available'], user.pw_name, s)
		dst = os.path.join(cfg['nginx:sites_enabled'], user.pw_name, s)

		if os.path.isfile(src):
			if os.path.exists(dst):
				ret.append({'message': 'Site %s is already enabled' % s})
			else:
				reload_nginx = True
				os.symlink(src, dst)
				ret.append({'message': 'Site %s enabled' % s})
		else:
			ret.append({'message': 'No site called %s' % s})
	
	if reload_nginx:
		devnull = open('/dev/null', 'w')
		subprocess.call(cfg['nginx:reload_cmd'].split(' '), stdout=devnull)
		
	return json.dumps(ret)

def site_disable(args):
	sites = args[1:]
	reload_nginx = False
	ret = []

	for s in sites:
		dst = os.path.join(cfg['nginx:sites_enabled'], user.pw_name, s)
		if os.path.exists(dst):
			reload_nginx = True
			os.unlink(dst)
			ret.append({ 'message': 'Site %s disabled' % s})
		else:
			ret.append({'message': 'Site %s is already disabled' % s})

	if reload_nginx:
		devnull = open('/dev/null', 'w')
		subprocess.call(cfg['nginx:reload_cmd'].split(' '), stdout=devnull)
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

def site_add(args):
	_help = 'Format: add <php> <domain> [<domainn> ...]'

	if len(args) < 3:
		return _help
	
	conf = {}
	if args[1] == 'php':
		conf = _parse_config('modules/nginx/php.tpl')['%domain%']
		conf['locations']['~ \.php?$']['fastcgi_pass'] = 'unix:/var/lib/darkadmin/php/%s.sock' % (user.pw_name)

	conf['server_name'] = ' '.join(args[2:])
	conf['root']        = '%s/sites/%s' % (user.pw_dir, args[2])
	conf['access_log']  = '/var/log/nginx/%s/%s/access.log' % (user.pw_name, args[2])
	conf['error_log']   = '/var/log/nginx/%s/%s/error.log' % (user.pw_name, args[2])

	fdata = _compose_config({args[2] : conf})
	fname = os.path.join(cfg['nginx:sites_available'], user.pw_name, args[2])
	f = open(fname, 'w')
	f.write(fdata)
	f.close()

	r = site_enable(['json', args[2]])

	return "Added %s\n%s" % (args[1], r)

def site_remove(args):
	r = site_disable(['json', args[1]])

	fname = os.path.join(cfg['nginx:sites_available'], user.pw_name, args[1])
	os.unlink(fname)
	return "Deleted %s\n%s" % (args[1], r)

def _compose_config(config):
	data = \
	    "server {\n" 
	
	sortby = [
		'server_name',
		'listen',
		'root',
		'-',
		'access_log',
		'error_log',
		'-',
		'locations',
	]

	sortbyid = 0

	for site, c in config.iteritems():
		dothis = True
		while dothis == True:
			for var, val in c.iteritems():
				if sortbyid >= len(sortby):
					dothis = False
					continue

				if sortby[sortbyid] == '-':
					data += '\n'
					sortbyid += 1
					continue

				if var != sortby[sortbyid]:
					continue

				if val == None or val == [] or val == {}:
					continue

				if var == 'locations':
					i = 0
					for name, location in val.iteritems():
						i += 1
						data += "\tlocation %s {\n" % name
						for var, val in location.iteritems():
							if val == None or val == [] or val == {}:
								continue
							data += "\t\t%s %s;\n" % (var, val)
						data += "\t}\n"
						if i < len(location) - 1:
							data += "\n"
				else:
					data += '\t%s %s;\n' % (var, val)

			sortbyid += 1

	data += "}"

	return data

def _parse_config(config):
	data = {}
	_srv = False
	_level = 0

	server = None
	server_data = []

	location = None

	for l in open(config):
		if _level < 0:
			err("Error while parsing config %s" % config)
			return {}

		l = l.strip().replace('\n', '')

		# dont parse comments
		l = re.sub('#(.*)$', '', l)

		m = re.match('^(.*){$', l)
		if m:
			_level += 1

		m = re.match('^server\s+{$', l)
		if m:
			server = None
			server_data = {
				'locations' : {},
				'fastcgi_params':{},
			}
			_srv = True
			continue

		m = re.match('^location\s+(.+)\s+{$', l)
		if m:
			location = m.group(1)
			server_data['locations'][location] = {'fastcgi_params':{}}
			continue

		m = re.match('^}$', l)
		if m:
			_level -= 1
			if location:
				location = None
			if _level == 0:
				data[server] = ''
				data[server] = server_data
				_srv = False
			continue

		m = re.match('^(\w+)\s+(.*)$', l)
		if m:
			val = m.group(2).split('\s')[0].replace(';', '')
			if location:
				if m.group(1) == 'fastcgi_param':
					server_data['locations'][location]['fastcgi_params'][val.split()[0]] = val.split()[1]
				else:
					server_data['locations'][location][m.group(1)] = val
			else:
				if m.group(1) == 'fastcgi_param':
					server_data['fastcgi_params'][val.split()[0]] = val.split()[1]
				else:
					server_data[m.group(1)] = val
				if m.group(1) == 'server_name':
					server = val
	
	if _level < 0:
		err("Error while parsing config %s" % config)
		return {}

	return data
