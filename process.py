from flask import jsonify

def process(req):
	params = req['params']
	proc = {"signup":		signup(params), 
			"signin":		signin(params), 
			"signout":		signout(params),
			"sendMessage":	sendMessage(params),
			"getMessages":	getMessages(params),
			"createGame":	createGame(params),
			"leaveGame":	leaveGame(params),
			"getGames":		getGames(params),
			"joinGame":		joinGame(params),
			"loadMap":		loadMap(params),
			}
	return proc.get(req['action'])

def signup(par):
	return par['password']
	
def signin(par):
	return par['login']
	
def signout(par):
	return par['login']
	
def sendMessage(par):
	return par['login']
	
def getMessages(par):
	return par['login']
	
def createGame(par):
	return par['login']

def leaveGame(par):
	return par['login']
	
def getGames(par):
	return par['login']
	
def joinGame(par):
	return par['login']
	
def loadMap(par):
	return par['login']
