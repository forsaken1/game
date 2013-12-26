EPS = 1e-6
TICK = 30
TESTING = True
LOGGING = True
writer = open("log_serv", "w").write
def log(msg):
	writer(msg+'\n')