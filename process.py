from flask import jsonify
import MySQLdb, re, os, hashlib

class Process:
	def __init__(self, app):
		if app.config["TESTING"]:
			db = 'test'
		else:
			db = 'game'
		self.db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=db)
		
	def __del__(self):
		self.db.close()
		
	def hash(self, body):
		m = hashlib.sha256()
		m.update(body)
		return m.hexdigest()
		
	def is_auth(self, sid):
		if not sid:
			return False
		cur = self.db.cursor()
		cur.execute('SELECT id FROM users WHERE sid = %s', (sid,))
		return cur.fetchone()
		
	def game_exists(self, gid):
		if not gid or gid != '':
			return False
		cur = self.db.cursor()
		cur.execute('SELECT id FROM games WHERE id = %s', (gid,))
		return cur.fetchone()
		
	def valid_name(self, name):
		return re.compile('^\w{1,64}$', re.IGNORECASE).match(name)
	
	def process(self, req):
		if not req.has_key('action') or not req.has_key('params'):
			return self.unknownAction()
		
		params = req['params']
		proc = 	{
			'signup': self.signup,
			'signin': self.signin,
			'signout': self.signout,
			'sendMessage': self.sendMessage,
			'getMessages': self.getMessages,
			'createGame': self.createGame,
			'leaveGame': self.leaveGame,
			'getGames': self.getGames,
			'joinGame': self.joinGame,
			'loadMap': self.loadMap,
		}
		if  not proc.has_key(req['action']):
			return self.unknownAction()
		
		return proc.get(req['action'])(params)

	def signup(self, par):
		if not re.compile('^\w{4,40}$', re.IGNORECASE).match(par['login']):
			return jsonify(result='badLogin', message='Bad login')
		
		if not re.compile('^\w{4,256}$', re.IGNORECASE).match(par['password']):
			return jsonify(result='badPassword', message='Bad password')
		
		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE login = %s', (par['login'],))
		if cur.fetchone():
			return jsonify(result='userExists', message='User exists')
		
		cur.execute('INSERT INTO users (login, password) VALUES (%s, %s)', (par['login'], self.hash(par['password']),))
		self.db.commit()
		return jsonify(result='ok', message='Successful signup')
		
	def signin(self, par):
		if not par.has_key('login') or not par.has_key('password'):
			return jsonify(result='incorrect', message='Incorrect login/password')
		
		cur = self.db.cursor()
		cur.execute('SELECT id FROM users WHERE login = %s AND password = %s', (par['login'], self.hash(par['password']),))
		res = cur.fetchone()
		if not res:
			return jsonify(result='incorrect', message='Incorrect login/password')
		
		ssid = self.hash(os.urandom(32) + 'key' + self.hash(os.urandom(32)))
		cur.execute("UPDATE users SET online = '1', sid = %s WHERE id = %s", (ssid,res[0],))
		self.db.commit()
		return jsonify(result='ok', sid=ssid, message='Successful signin')
		
	def signout(self, par):
		if self.is_auth(par['sid']):
			sid = par['sid']
			self.db.cursor().execute('UPDATE users SET online = 0, sid = "" WHERE sid = %s', (sid,))
			self.db.commit()
			return jsonify(result='ok', message='Successful signout')
		else:
			return jsonify(result='badSid', message='Wrong session id')
		
	def sendMessage(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		if not par.has_key('game') or (par['game'] != '' and not self.game_exists(par['game'])):
			return jsonify(result='badGame', message='Wrong game id')
		
		sid = par['sid']
		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))
		login = cur.fetchone()
		text = par['text']
		game = par['game']
		cur.execute('INSERT INTO messages (login, text, time, game_id) VALUES (%s, %s, UNIX_TIMESTAMP(), %s)', (login, text, game,))
		self.db.commit()
		return jsonify(result='ok', message='Your message added')
		
	def getMessages(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
			
		if not par.has_key('game') or (par['game'] != '' and not self.game_exists(par['game'])):
			return jsonify(result='badGame', message='Wrong game id')
		
		if not par.has_key('since'):
			since = 0
		else:
			since = par['since']
		
		cur = self.db.cursor()
		m = cur.execute('SELECT time, text, login FROM messages WHERE time > %s ORDER BY time', (since,))
		return jsonify(result='ok', message='All messages', messages=m)
		
	def createGame(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		if not self.valid_name(par['name']):
			return jsonify(result='badName', message='Incorrect game name')
		
		if self.game_exists(par['game']):
			return jsonify(result='gameExists', message='Game already exists')
			
		if not self.valid_name(par['map']):
			return jsonify(result='badMap', message='Incorrect map name')
			
		if not par['maxPlayers']:
			return jsonify(result='badMaxPlayers', message='Incorrect max players')
		
		cur = self.db.cursor()
		cur.execute('INSERT INTO games (name, map, maxPlayers, status, creator_sid) VALUES(%s, %s, %s, 1, %s)', (par['name'], par['map'], par['maxPlayers'], par['sid']))
		game_id = cursor.lastrowid
		cur.execute('UPDATE users SET game_id = %s WHERE sid = %s', (game_id, par['sid']))
		self.db.commit()
		return jsonify(result='ok', message='Game successfully created')
	
	def getGames(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
			
		cur = self.db.cursor()
		cur.execute('SELECT id, sid, name, map, maxPlayers, status FROM games')
		res = cur.fetchall()
		for item in res:
			cur.execute('SELECT login FROM users WHERE game_id = %s', (item['id'],))
			item['players'] = cur.fechall()
		
		return jsonify(result='ok', games=res, message='All games')
		
	def joinGame(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		if not self.game_exists(par['game']):
			return jsonify(result='badGame', message='Incorrect game id')
		
		cur = self.db.cursor()
		cur.execute('SELECT id, playersCount, maxPlayers FROM games WHERE name = %s', (par['game'],))
		res = cut.fetchone()
		if res['playersCount'] >= res['maxPlayers']:
			return jsonify(result='gameFull', message='Game full')
			
		cur.execute('UPDATE games SET playersCount = %s WHERE name = %s', (res['playersCount'] + 1, par['game']))
		cur.execute('UPDATE users SET game_id = %s WHERE sid = %s', (res['id'], par['sid']))
		self.db.commit()
		return jsonify(result='ok', message='You joined')
		
	def leaveGame(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		cur = self.db.cursor()
		cur.execute('SELECT game_id FROM users WHERE sid = %s', (par['sid'],))
		cur.execute('SELECT id FROM games WHERE id = %s AND status = "2"')
		if not cur.fetchone():
			return jsonify(result='notInGame', message='Player not in game')
		
		cur.execute('SELECT id, playersCount, maxPlayers FROM games WHERE name = %s', (par['game'],))
		res = cut.fetchone()
		cur.execute('UPDATE games SET playersCount = %s WHERE name = %s', (res['playersCount'] - 1, par['game']))
		cur.execute('UPDATE users SET game_id = %s WHERE sid = %s', (0, par['sid']))
		self.db.commit()
		return jsonify(result='ok', message='Success leave from game')
	
	def loadMap(self, par):
		return jsonify(result='ok', message='OK')

	def unknownAction(self):
		return jsonify(result='unknownAction', message='Unknown action')
