#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, socket, time
import struct

cfg = {
	'sockfile' : 'darkadmin.sock',
	'uid_min'  : 1000,
}

SO_PEERCRED = 17

def log(msg):
	print("[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), msg))

def main():
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

	try:
		os.remove(cfg['sockfile'])
	except OSError:
		pass

	try:
		sock.bind(cfg['sockfile'])
	except socketerror, e:
		print "Can't create socket:\n%s" % e
		sys.exit(1)

	os.chmod(cfg['sockfile'], 0666)

	sock.listen(5)

	while 1:
		(client, addr) = sock.accept()

		# get unix credential
		creds = client.getsockopt(socket.SOL_SOCKET, SO_PEERCRED, struct.calcsize('3i'))
		pid, uid, gid = struct.unpack('3i', creds)

		if not uid:
			client.send("Access Denied!")
			log("WARN: UID not defined")
			client.close()
			continue

		# check credentials
		if uid < cfg['uid_min'] or uid > 65000:
			client.send("Access Denied!")
			log("WARN: UID %s is not allowed to use darkadmin" % uid)
			client.close()
			continue

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
