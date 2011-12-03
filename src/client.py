#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, socket, sys

cfg = {
	'sockfile' : 'darkadmin.sock',
}

SO_PASSCRED = 16

def main():
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, SO_PASSCRED, 1)
	try:
		sock.connect(cfg['sockfile'])
	except socket.error, e:
		print "Can't connect to socket"
		sys.exit(1)
	try:
		sys.argv[0] = 'cli'
		sock.send(' '.join(sys.argv))
		data = sock.recv(1024)
		print data
	except socket.error, e:
		# daemon sends error message to client
		# show it
		print sock.recv(1024)
		

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print "\033[1G\033[K\033[1;37mExiting... (\033[0mCtrl+C\033[1;37m)"
