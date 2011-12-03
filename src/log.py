import time

def log(msg):
	print("[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()), msg))
