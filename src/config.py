# -*- coding: utf-8 -*-

import re

def read(conf = '/etc/darkadmin/main.conf'):
	cfg = {}
	f = file(conf, 'r');
	while True:
		l = f.readline()
		if not l:
			break

		l = l.replace('\n', '').strip()
		l = re.sub('#(.*)', '', l)

		if l:
			m = re.match(r'^([\S]+)\s+(.+)$', l)
			if m:
				if m.group(2).isdigit():
					cfg[m.group(1)] = int(m.group(2))
				else:
					cfg[m.group(1)] = m.group(2)
	return cfg
