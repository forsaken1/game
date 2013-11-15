from flask import jsonify
from exceptions import Exception
import MySQLdb, re, os, hashlib, time, json

MAXLOGIN = 40
MINLOGIN = 4
LONGBLOB = 65535

class param_validator:
	
	def valid_str(self, str, min = 1, max = 255):
		if type(str) == unicode and min <= len(str) <= max and all(ord(c) < 128 for c in str):
			return True
		else: return False	
		
	def badLogin(self, login):
		return self.valid_str(login, MINLOGIN, MAXLOGIN)
		
	def badPassword(self, password):
		return self.valid_str(password, MINLOGIN, LONGBLOB)
		
	def badSid(self, sid):
		if not self.valid_str(sid): return False
		cur = self.db.cursor()
		cur.execute('SELECT id FROM users WHERE sid = %s', (sid,))
		return cur.fetchone()		

	def badName(self, name):
		return self.valid_str(name)
		
	def badGame(self, game):											### '' is valid game too
		cur = self.db.cursor()
		if game == '':
			return True			
		cur.execute('SELECT id FROM games WHERE id = %s', (game,))
		if type(game) != int or not cur.fetchone():
			return False
		else: return True
		
	def badText(self, text):
		if type(text) != unicode or len(text) > LONGBLOB:		
			return False
		return True
	
	def badSince(self, since):
		if type(since) != int or since < 0:
			return False
		else: return True
	
	def badMapId(self, map):
		cur = self.db.cursor()	
		cur.execute('SELECT id FROM maps WHERE id = %s', (map,))
		if type(map) != int or not cur.fetchone():
			return False
		else: return True		
			
	def badMaxPlayers(self, maxPlayers):
		if type(maxPlayers) != int or maxPlayers < 0:
			return False
		else: return True		

	def valid_dot(self, c):
		return 'A'<=c<='z' or '0'<=c<='9' or c=='.' or c=='$' or c=='#' 
	
	def badMap(self, map):
		if type(map) != list or len(map) < 1: return False
		size = len(map[0])
		for row in map:
			if type(row) != unicode or len(row) != size or not all(self.valid_dot(d) for d in row):
				return False
		return True
		
	def __init__(self, db):
		self.db = db
		self.param_error = {
			'login': 		'badLogin',
			'password': 	'badPassword',
			'sid': 			'badSid',
			'name': 		'badName',
			'game': 		'badGame',
			'text': 		'badText',
			'since': 		'badSince',
			'map': 			'badMap',
			'maxPlayers': 	'badMaxPlayers'
		}
	
	def find_error(self, formal, actual):
		for param in formal:
			if param == 'mapId':	
				if not self.badMapId(actual['map']):
					return "badMap"
				else: continue
			if not getattr(self, self.param_error[param])(actual[param]):
				return self.param_error[param]
		return None		

class Process:		

	def __init__(self, app):
		db_name = 'game'
		self.db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=db_name)
		self.valid = param_validator(self.db)
		
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
		
	def user_info(self, sid):
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))
		return cur.fetchone()
		
	def process(self, req):
		try:
			req = json.loads(req)
		except ValueError:
			return jsonify(result='badJSON', message='request is not JSON')
		try:
			if req['action'] == 'startTesting':
				return self.start_testing()
			proc = {
				'signup': 		[self.signup, 			['login', 'password']],
				'signin': 		[self.signin, 			['login', 'password']],
				'signout': 		[self.signout, 			['sid']],
				'sendMessage': 	[self.send_message, 	['sid', 'game', 'text']],
				'getMessages': 	[self.get_messages, 	['sid', 'game', 'since']],
				'createGame': 	[self.create_game, 		['sid', 'name', 'mapId', 'maxPlayers']],
				'getGames': 	[self.get_games, 		['sid']],
				'joinGame': 	[self.join_game, 		['sid', 'game']],
				'leaveGame': 	[self.leave_game, 		['sid']],
				'uploadMap': 	[self.upload_map, 		['sid', 'name', 'map', 'maxPlayers']],
				'getMaps': 		[self.get_maps, 		['sid']],
				'sidValidation': [self.sidValidation,   ['sid']],
			}
			action = proc[req['action']]		
		except KeyError:
			return jsonify(result='unknownAction', message='Unknown action')
			

		params = req['params']
		
		try: error = self.valid.find_error(action[1], params)
		except KeyError: return jsonify(result='paramMissed ', message='Not enough params')		
		if error:
			if action[0] == self.signin:
				return jsonify(result= 'incorrect', message='param error') 
			else:
				return jsonify(result= error, message='param error') 
		return action[0](params)


	def sidValidation(self, par):
		cur = self.db.cursor()
		cur.execute('SELECT sid FROM users WHERE sid = %s', (par['sid'],))
		if not cur.fetchone():
			return jsonify(result='ok')

		return jsonify(result='invalidSid')
	
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
	
	def signup(self, par):															# add consist proofer
		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE login = %s', (par['login'],))
		if cur.fetchone():
			return jsonify(result='userExists', message='User exists')
		
		cur.execute('INSERT INTO users (login, password) VALUES (%s, %s)', (par['login'], self.hash(par['password']),))
		self.db.commit()
		return jsonify(result='ok', message='Successful signup')
	
	def signin(self, par):		
		cur = self.db.cursor()
		cur.execute('SELECT id FROM users WHERE login = %s AND password = %s', (par['login'], self.hash(par['password']),))
		res = cur.fetchone()
		if not res:
			return jsonify(result='incorrect', message='Incorrect login/password')
		
		ssid = self.hash(os.urandom(32) + 'key' + self.hash(os.urandom(32)))
		cur.execute("UPDATE users SET sid = %s WHERE id = %s", (ssid,res[0],))
		self.db.commit()
		return jsonify(result='ok', sid=ssid, message='Successful signin')
		
	def signout(self, par):
		sid = par['sid']
		self.leave_game({'sid': sid})
		
		self.db.cursor().execute('UPDATE users SET sid = NULL WHERE sid = %s', (sid,))
		self.db.commit()
		return jsonify(result='ok', message='Successful signout')
		
	def send_message(self, par):
		sid , gid, text = par['sid'], par['game'], par['text']
		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))
		login = cur.fetchone()[0]
		query = 'INSERT INTO messages (login, text, time, game_id) VALUES (%s, %s, UNIX_TIMESTAMP(),'+(str(gid) if gid else "NULL")+')'
		cur.execute(query, (login, text,))
		self.db.commit()
		return jsonify(result='ok', message='Your message added')
		
	def get_messages(self, par):
		gid, since = par['game'], par['since']
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		query = 'SELECT time, text, login FROM messages WHERE time >= %s AND game_id '+('='+str(gid) if gid else "IS NULL")+' ORDER BY time'
		cur.execute(query, (since, ))
		mess = cur.fetchall()
		return jsonify(result='ok', message='All messages', messages=mess)
		
	def create_game(self, par):
		sid = par['sid']
			
		cur = self.db.cursor()			
		cur.execute('SELECT id FROM games WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return jsonify(result='gameExists', message='Game exists')		

		cur.execute('SELECT maxPlayers FROM maps WHERE id = %s', (par['map'],))
		mapMax = cur.fetchone()[0]
			
		if mapMax < par['maxPlayers']:
			return jsonify(result='badMaxPlayers', message='Max players more than map avaible')
		
		cur = self.db.cursor()
		cur.execute("INSERT INTO games (name, map, maxPlayers) VALUES(%s, %s, %s)", (par['name'], par['map'], par['maxPlayers']))
		self.db.commit()
		ret = self.join_game({'sid': sid, 'game': cur.lastrowid})
		if json.loads(ret.data)['result'] == 'ok':
			return jsonify(result='ok', message='Game created')				
		else: 
			cur.execute("DELETE FROM games WHERE name = %s", (par['name'],))
			self.db.commit()		
			return ret
		
	def get_games(self, par):
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT id, name, map, maxPlayers, status FROM games')	
		res = cur.fetchall()	
		for item in res:
			item['status'] = 'running' if item['status'] else 'finished' 
			cur.execute('SELECT login FROM user_game WHERE game_id = %i ORDER BY id' %item['id'])
			players = cur.fetchall()
			item['players'] = []			
			for player in players:
				item['players'].append(player['login'])
		return jsonify(result='ok', games=res, message='All games')
		
	def join_game(self, par):
		sid = par['sid']		
		cur = self.db.cursor()
		if par['game'] == "":
			return jsonify(result='badGame', message='Game is ""')			
		cur.execute('SELECT id FROM user_game WHERE sid = %s', (sid,))
		if cur.fetchone():
			return jsonify(result='alreadyInGame', message='User already in game')					
			
		cur.execute('SELECT maxPlayers FROM games WHERE id = %s', (par['game'],))
		maxPlayers = cur.fetchone()[0]
		cur.execute('SELECT count(*) FROM user_game WHERE game_id = %s', (par['game'],))
		playersCount = cur.fetchone()[0]
		if playersCount >= maxPlayers:
			return jsonify(result='gameFull', message='Game full')
			
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))	
		login = cur.fetchone()[0]
		cur.execute('INSERT INTO user_game (sid, login, game_id) VALUES(%s, %s, %s)', (sid, login, par['game']))
		self.db.commit()
		return jsonify(result='ok', message='You joined to game')
		
	def leave_game(self, par):		
		cur = self.db.cursor()
		cur.execute('SELECT game_id FROM user_game WHERE sid = %s', (par['sid'],))
		game = cur.fetchone()
		if not game: 
			return jsonify(result='notInGame', message='Player not in game')
		game = game[0]			
		
		cur.execute('DELETE from user_game WHERE sid = %s', (par['sid'], ))
		self.db.commit()
		
		cur.execute('SELECT count(*) FROM user_game WHERE game_id = %s', (game,))
		if not cur.fetchone()[0]:
			cur.execute('DELETE from games WHERE id = %s', (game,))			
		self.db.commit()
		return jsonify(result='ok', message='You left game') 
	
	def upload_map(self, par):			
		cur = self.db.cursor()
		cur.execute('SELECT id FROM maps WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return jsonify(result='mapExists', message='Map already exists')
		strmap = ''
		for row in par['map']:
			strmap += row + '\n'
		strmap = strmap[:-1]
		cur.execute("INSERT INTO maps (name, map, maxPlayers) VALUES(%s, %s, %s)", (par['name'], strmap, par['maxPlayers']))
		self.db.commit()
		return jsonify(result='ok', message='Your map added')

	def get_maps(self, par):			
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT id, name, map, maxPlayers FROM maps')	
		res = cur.fetchall()
		for map in res:
			map['map'] = map['map'].split('\n')
			
		return jsonify(result='ok', maps=res, message='All maps')

