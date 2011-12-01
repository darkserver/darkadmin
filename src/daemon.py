#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, socket
import struct

cfg = {
	'sockfile' : 'darkadmin.sock',
}

SO_PEERCRED = 17

def main():
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

	try:
		os.remove(cfg['sockfile'])
	except OSError:
		pass
	sock.bind(cfg['sockfile'])
	os.chmod(cfg['sockfile'], 0666)

	sock.listen(5)

	while 1:
		(client, addr) = sock.accept()

		# get unix credential
		creds = client.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize('3i'))
		pid, uid, gid = struct.unpack('3i', creds)

		data = client.recv(1024)
		if not data:
		 	break
		print data
		client.send('world')

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		os.remove(cfg['sockfile'])
		print "\033[1G\033[K\033[1;37mExiting... (\033[0mCtrl+C\033[1;37m)"
