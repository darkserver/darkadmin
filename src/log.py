import time

def log(msg):
	print("[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), msg))

def warn(msg):
	print("[%s] \033[1;33m%s\033[0m" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), msg))

def err(msg):
	print("[%s] \033[1;31m%s\033[0m" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), msg))
