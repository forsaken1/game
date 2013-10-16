from flask import jsonify
import MySQLdb, re, os, hashlib, time, json

class Process:		
	def create_db(self):
		con = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='')	
		cursor = con.cursor()
		db_name = "game"
		cursor.execute('CREATE DATABASE IF NOT EXISTS %s'% db_name)
		cursor.execute('use ' + db_name)   
		sql = '''CREATE TABLE IF NOT EXISTS `users` (
				`id` int(11) NOT NULL AUTO_INCREMENT,
				`online` bit(1) DEFAULT b'0' NOT NULL,
				`sid` varchar(64) CHARACTER SET latin1,
				`login` varchar(255) CHARACTER SET latin1 NOT NULL,
				`password` varchar(255) CHARACTER SET latin1 NOT NULL,
				`game_id` int(11) DEFAULT NULL,
				`last_connection` date,
				PRIMARY KEY (`id`),
				KEY `id` (`id`)
				)DEFAULT CHARSET=utf8 AUTO_INCREMENT=2;        
			   '''
		cursor.execute(sql)    
		sql = '''CREATE TABLE IF NOT EXISTS `messages` (
				`id` int(11) NOT NULL AUTO_INCREMENT,
				`login` varchar(255) CHARACTER SET latin1 NOT NULL,
				`text` varchar(1024) CHARACTER SET utf8 NOT NULL,
				`time` int(11) NOT NULL,
				`game_id` int(11),
				PRIMARY KEY (`id`)
				)DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;    
			   '''
		cursor.execute(sql)             
		sql = '''CREATE TABLE IF NOT EXISTS `games` (
				`id` int(11) NOT NULL AUTO_INCREMENT,
				`name` varchar(256) CHARACTER SET latin1 NOT NULL,
				`map` varchar(256) CHARACTER SET latin1 NOT NULL,
				`maxPlayers` int(11) NOT NULL,
				`status` bit(1) DEFAULT b'0' NOT NULL,
				`sid` varchar(64) NOT NULL,
				PRIMARY KEY (`id`)
				)DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;   
			   '''
		cursor.execute(sql)        
		con.close()
		
	def __init__(self, app):
		self.create_db()	
		db_name = 'game'
		self.db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=db_name)
		
	def __del__(self):
		self.db.close()
	
	def config(self):
		config = open("conf", "r").read()
		config = '{"' + config.replace('\n', '","').replace(': ', '": "') + '"}'
		return json.loads(config)	
	
	def hash(self, body):
		m = hashlib.sha256()
		m.update(body)
		return m.hexdigest()
		
	def is_auth(self, sid):
		if not sid:
			return False
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT id, game_id FROM users WHERE sid = %s', (sid,))
		return cur.fetchone()
		
	def game_exists(self, gid):
		if not gid:
			return False
		cur = self.db.cursor()
		cur.execute('SELECT id FROM games WHERE id = %s', (gid,))
		return cur.fetchone()
		
	def valid_name(self, name):
		if name: return re.compile('^\w{1,64}$', re.IGNORECASE).match(name)
		else: return False
		
	def process(self, req):
		if not req.has_key('action'):
			return self.unknown_action()
		if req['action'] == 'startTesting':
			return self.start_testing()
		proc = 	{
			'signup': self.signup,
			'signin': self.signin,
			'signout': self.signout,
			'sendMessage': self.send_message,
			'getMessages': self.get_messages,
			'createGame': self.create_game,
			'leaveGame': self.leave_game,
			'getGames': self.get_games,
			'joinGame': self.join_game,
			'loadMap': self.load_map
		}
		if  not proc.has_key(req['action']) or not req.has_key('params'):
			return self.unknown_action()
		params = req['params']		
		return proc.get(req['action'])(params)
	
	def start_testing(self):
		data = open("conf", "r").read()
		if (self.config()['testing'] != 'yes'):
			return jsonify(result='notInTestMode')
		cursor = self.db.cursor()
		cursor.execute('show tables')
		tables = cursor.fetchall()
		for table in tables:
			cursor.execute('truncate %s' %table)
		return jsonify(result='ok')
	
	def signup(self, par):
		if not (4 <= len(par['login']) <= 40 and all(ord(c) < 128 for c in par['login'])):
			return jsonify(result='badLogin', message='Bad login')
		
		if not (4 <= len(par['password']) <= 256 and all(ord(c) < 128 for c in par['password'])):
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
		cur.execute("UPDATE users SET online = b'1', sid = %s WHERE id = %s", (ssid,res[0],))
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
		
	def send_message(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		if not par.has_key('game') or (par['game'] != '' and not self.game_exists(par['game'])):
			return jsonify(result='badGame', message='Wrong game id')
		
		sid , gid = par['sid'], par['game']
		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))
		login = cur.fetchone()[0]
		text = par['text']
		query = 'INSERT INTO messages (login, text, time, game_id) VALUES (%s, %s, UNIX_TIMESTAMP(),'+(str(gid) if gid else "NULL")+')'
		cur.execute(query, (login, text,))
		self.db.commit()
		return jsonify(result='ok', message='Your message added')
		
	def get_messages(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
			
		if not par.has_key('game') or (par['game'] != '' and not self.game_exists(par['game'])):
			return jsonify(result='badGame', message='Wrong game id')
		gid = par['game']
		if not par.has_key('since'):		#sure needed?!
			since = 0
		else:
			since = par['since']
			if not isinstance(since, int):
				return jsonify(result='badSince', message='Incorrect since time')
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		query = 'SELECT time, text, login FROM messages WHERE time >= %s AND game_id '+('='+str(gid) if gid else "IS NULL")+' ORDER BY time'
		cur.execute(query, (since, ))
		mess = cur.fetchall()
		return jsonify(result='ok', message='All messages', messages=mess)
		
	def create_game(self, par):
		user = self.is_auth(par['sid'])
		if not user:
			return jsonify(result='badSid', message='Wrong session id')

		if user['game_id']:
			return jsonify(result='alreadyInGame', message='Host already in game')
			
		if not self.valid_name(par['name']):
			return jsonify(result='badName', message='Incorrect game name')
			
		if not self.valid_name(par['map']): #map id
			return jsonify(result='badMap', message='Incorrect map name')
			
		if not par['maxPlayers'] or not isinstance(par['maxPlayers'], int):
			return jsonify(result='badMaxPlayers', message='Incorrect max players')

		cur = self.db.cursor()			
		cur.execute('SELECT name FROM games WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return jsonify(result='gameExists', message='Game exists')		

		cur = self.db.cursor()
		cur.execute("INSERT INTO games (name, map, maxPlayers, status, sid) VALUES(%s, %s, %s, b'1', %s)", (par['name'], par['map'], par['maxPlayers'], par['sid']))
		game_id = cur.lastrowid
		sid = par['sid']
		cur.execute('UPDATE users SET game_id = %s WHERE sid = %s', (game_id, sid))
		self.db.commit()
		return jsonify(result='ok', message='Game successfully created')
	
	def get_games(self, par):	
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
			
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT id, name, map, maxPlayers, status FROM games')	
		res = cur.fetchall()	
		for item in res:
			item['status'] = 'running' if item['status'] else 'finished' 
			item['players'] = []			
			cur.execute('SELECT login FROM users WHERE game_id = %i' %item['id'])
			players = cur.fetchall()
			for i in range(len(players)):
				item['players'].append(players[i]['login'])
		return jsonify(result='ok', games=res, message='All games')			# change bool status to str
		
	def join_game(self, par):
		user = self.is_auth(par['sid'])
		if not user:
			return jsonify(result='badSid', message='Wrong session id')
		
		if user['game_id']:
			return jsonify(result='alreadyInGame', message='User already in game')			
		
		if not self.game_exists(par['game']):
			return jsonify(result='badGame', message='Incorrect game id')
		
		cur = self.db.cursor()
		cur.execute('SELECT maxPlayers FROM games WHERE id = %s', (par['game'],))
		res = cur.fetchone()
		cur.execute('SELECT id FROM users WHERE game_id = %s', (par['game'],))
		_res = cur.fetchall()
		playersCount = len(_res)
		if playersCount >= res[0]:
			return jsonify(result='gameFull', message='Game full')
		cur.execute('UPDATE users SET game_id = %s WHERE sid = %s', (par['game'], par['sid']))
		self.db.commit()
		return jsonify(result='ok', message='You joined')
		
	def leave_game(self, par):
		if not self.is_auth(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		cur = self.db.cursor()
		cur.execute('SELECT game_id FROM users WHERE sid = %s', (par['sid'],))
		gid = cur.fetchone()[0]
		if not gid:
			return jsonify(result='notInGame', message='Player not in game')					
		cur.execute('UPDATE users SET game_id = NULL WHERE sid = %s', (par['sid'], ))
		self.db.commit()
		return jsonify(result='ok', message='Success leave from game')
	
	def load_map(self, par):
		return jsonify(result='ok', message='OK')

	def unknown_action(self):
		return jsonify(result='unknownAction', message='Unknown action')
