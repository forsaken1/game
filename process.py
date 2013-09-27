from flask import jsonify, session
import MySQLdb, re, os, hashlib

class Process:
	def __init__(self):
		self.db = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='', db='game')
		
	def __del__(self):
		self.db.close()
		
	def md5(self, body):
		m = hashlib.md5()
		m.update(body)
		return m.hexdigest()
	
	def process(self, req):
		if not req['params']:
			return self.unknownAction()
		
		params = req['params']
		proc = 	{
			'signup':		self.signup,
			'signin':		self.signin,
			'signout':		self.signout,
			'sendMessage':	self.sendMessage,
			'getMessages':	self.getMessages,
			'createGame':	self.createGame,
			'leaveGame':	self.leaveGame,
			'getGames':		self.getGames,
			'joinGame':		self.joinGame,
			'loadMap':		self.loadMap,
		}
		if not proc.has_key(req['action']):
			return self.unknownAction()
		
		return proc.get(req['action'])(params)

	def signup(self, par):
		reg_exp_login = re.compile('\w{4,40}', re.IGNORECASE)
		result = reg_exp_login.match(par['login'])
		if not result:
			return jsonify(result='badLogin', message='Bad login')
		
		reg_exp_pass = re.compile('\w{4,}', re.IGNORECASE)
		result = reg_exp_pass.match(par['password'])
		if not result:
			return jsonify(result='badPassword', message='Bad password')
		
		cur = self.db.cursor()
		cur.execute('SELECT login FROM user WHERE login = %s', (par['login'],))
		login = cur.fetchone()
		if login:
			return jsonify(result='userExists', message='User exists')
		
		cur.execute('INSERT INTO user (login, password) VALUES (%s, %s)', (par['login'], self.md5(par['password']),))
		self.db.commit()
		return jsonify(result='ok', message='Successful signup')
		
	def signin(self, par):
		cur = self.db.cursor()
		cur.execute('SELECT login FROM user WHERE login = %s AND password = %s', (par['login'], self.md5(par['password']),))
		login = cur.fetchone()
		if not login:
			return jsonify(result='incorrect', message='Incorrect login/password')
		
		session['sid'] = self.md5(os.urandom(32))
		session['login'] = login
		return jsonify(result='ok', sid=session['sid'], message='Successful signin')
		
	def signout(self, par):
		if par['sid'] == session['sid']:
			return jsonify(result='ok', message='Successful signout')
		else:
			return jsonify(result='badSid', message='Wrong session id')
		
	def sendMessage(self, par):
		if par['sid'] != session['sid']:
			return jsonify(result='badSid', message='Wrong session id')
			
		cur = self.db.cursor()
		cur.execute('INSERT INTO message (login, text, time, game_id) VALUES (%s, %s, TIME(), %s)', (session['login'], par['text'], par['game'],))
		return jsonify(result='ok', message='Your message added')
		
	def getMessages(self, par):
		if par['sid'] != session['sid']:
			return jsonify(result='badSid', message='Wrong session id')
			
		
		return jsonify(result='ok', message='All messages')
		
	def createGame(self, par):
		return par['login']

	def leaveGame(self, par):
		return par['login']
		
	def getGames(self, par):
		return par['login']
		
	def joinGame(self, par):
		return par['login']
		
	def loadMap(self, par):
		return par['login']

	def unknownAction(self):
		return jsonify(result='unknownAction', message='Unknown action')
