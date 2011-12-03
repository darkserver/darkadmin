import json

cfg = {}
user = None

'''
return format:
  status - internal status code
  reply  - send this to client
'''

def process(args, config, userdata):
	global cfg, user
	cfg = config
	user = userdata
	return {
		'somecommand' : somefunction,
	}.get(args[1], help)(args[:1] + args[2:])

def help(args):
	reply = \
		'Available commands:\n\n' \
		'  somecommand      it does something useless\n'
	return { 'status': 0, 'reply': reply }

def somefunction(args):
	data = {
		'usefull' : 1,
		'useless' : True,
	}
	reply = json.dumps(data)
	return { 'status': 0, 'reply': reply }
