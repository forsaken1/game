from flask import jsonify
from exceptions import Exception
import MySQLdb, re, os, hashlib, time, json

class Process:		
	def __init__(self, app):
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
		
	def user_info(self, sid):
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))
		return cur.fetchone()
		
	def game_exists(self, gid):
		if not gid:
			return False
		cur = self.db.cursor()
		cur.execute('SELECT id FROM games WHERE id = %s', (gid,))
		return cur.fetchone()
		
	def valid_name(self, name, min = 1, max = 255):
		if type(name) == unicode and min <= len(name) <= max and all(ord(c) < 128 for c in name):
			return True
		else: return False
		
	def process(self, req):
		try:
			req = json.loads(req)
		except ValueError:
			return jsonify(result='badJSON', message='request is not JSON')
		try:
			if req['action'] == 'startTesting':
				return self.start_testing()
			proc = {
				'signup': self.signup,
				'signin': self.signin,
				'signout': self.signout,
				'sendMessage': self.send_message,
				'getMessages': self.get_messages,
				'createGame': self.create_game,
				'leaveGame': self.leave_game,
				'getGames': self.get_games,
				'joinGame': self.join_game,
				'uploadMap': self.upload_map,
				'getMaps': self.get_maps
			}
			action = proc[req['action']]
		except KeyError:
			return jsonify(result='unknownAction', message='Unknown action')
			
		try:
			params = req['params']
			return action(params)
		except KeyError:
			return jsonify(result='paramMissed', message='Not enough parametrs') 
	
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
		if not self.valid_name(par['login'], 4, 40):
			return jsonify(result='badLogin', message='Bad login')
		
		if not self.valid_name(par['password'], 4):
			return jsonify(result='badPassword', message='Bad password')
		
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
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')		
		sid = par['sid']
		
		self.leave_game({'sid': sid})
		
		self.db.cursor().execute('UPDATE users SET sid = NULL WHERE sid = %s', (sid,))
		self.db.commit()
		return jsonify(result='ok', message='Successful signout')
		
	def send_message(self, par):
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
		if par['game'] != '' and not self.game_exists(par['game']):
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
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
			
		if par['game'] != '' and not self.game_exists(par['game']):
			return jsonify(result='badGame', message='Wrong game id')
		gid, since = par['game'], par['since']

		if not isinstance(since, int)  or since < 0:
			return jsonify(result='badSince', message='Incorrect since time')
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		query = 'SELECT time, text, login FROM messages WHERE time >= %s AND game_id '+('='+str(gid) if gid else "IS NULL")+' ORDER BY time'
		cur.execute(query, (since, ))
		mess = cur.fetchall()
		return jsonify(result='ok', message='All messages', messages=mess)
		
	def create_game(self, par):
		sid = par['sid']
		user = self.user_info(sid)
			
		if not self.valid_name(par['name']):
			return jsonify(result='badName', message='Incorrect game name')
			
		cur = self.db.cursor()			
		cur.execute('SELECT id FROM games WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return jsonify(result='gameExists', message='Game exists')		

		cur.execute('SELECT maxPlayers FROM maps WHERE id = %s', (par['map'],))
		mapMax = cur.fetchone()
		if not mapMax:
			return jsonify(result='badMap', message='Wrong map id')				
		mapMax = mapMax[0]			
			
		if not isinstance(par['maxPlayers'], int) or par['maxPlayers'] < 1 or mapMax < par['maxPlayers']:
			return jsonify(result='badMaxPlayers', message='Incorrect max players')
		
		cur = self.db.cursor()
		cur.execute("INSERT INTO games (name, map, maxPlayers) VALUES(%s, %s, %s)", (par['name'], par['map'], par['maxPlayers']))
		self.db.commit()
		ret = self.join_game({'sid': sid, 'game': cur.lastrowid})
		if json.loads(ret.data)['result'] == 'ok':
			return jsonify(result='ok', message='Game created')				
		else: return ret
		
	def get_games(self, par):	
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')

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
		user = self.user_info(sid)
		if not user:
			return jsonify(result='badSid', message='Wrong session id')
		if not self.game_exists(par['game']):
			return jsonify(result='badGame', message='Incorrect game id')
		
		cur = self.db.cursor()
		cur.execute('SELECT id FROM user_game WHERE sid = %s', (sid,))
		if cur.fetchone():
			return jsonify(result='alreadyInGame', message='User already in game')		
			
		cur.execute('SELECT maxPlayers FROM games WHERE id = %s', (par['game'],))
		maxPlayers = cur.fetchone()[0]
		cur.execute('SELECT count(*) FROM user_game WHERE game_id = %s', (par['game'],))
		playersCount = cur.fetchone()[0]
		if playersCount >= maxPlayers:
			return jsonify(result='gameFull', message='Game full')
			
		cur.execute('INSERT INTO user_game (sid, login, game_id) VALUES(%s, %s, %s)', (sid, user['login'], par['game']))
		self.db.commit()
		return jsonify(result='ok', message='You joined to game')
		
	def leave_game(self, par):							# remove game when last player leave it?
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
		
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
			cur.execute('DELETE from games WHERE id = %s', (game ))			
		return jsonify(result='ok', message='You left game') 
	
	def valid_char(self, c):
		return 'A'<=c<='z' or '0'<=c<='9' or c=='.' or c=='$' or c=='#' 
	
	def create_strmap(self, map):
		size = len(map[0])
		str = ""
		for row in map:
			if not all(self.valid_char(c) for c in row):
				raise Exception('incorrect consist')		
			if len(row) != size:
				raise Exception('incorrect row length: ', len(row))
			str += row + '\n'
		str = str[:-1]
		return str
	
	def upload_map(self, par):
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')	
		
		if not self.valid_name(par['name']):
			return jsonify(result='badName', message='Incorrect map name')
			
		if not isinstance(par['maxPlayers'], int) or par['maxPlayers'] < 1:
			return jsonify(result='badMaxPlayers', message='Incorrect max players')
			
		try:
			strmap = self.create_strmap(par['map'])
		except Exception as a:
			return jsonify(result="badMap", message='Incorrect map')				
		cur = self.db.cursor()
		cur.execute('SELECT id FROM maps WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return jsonify(result='mapExists', message='Map already exists')

		cur.execute("INSERT INTO maps (name, map, maxPlayers) VALUES(%s, %s, %s)", (par['name'], strmap, par['maxPlayers']))
		self.db.commit()
		return jsonify(result='ok', message='Your map added')

	def get_maps(self, par):
		if not self.user_info(par['sid']):
			return jsonify(result='badSid', message='Wrong session id')
			
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT id, name, map, maxPlayers FROM maps')	
		res = cur.fetchall()
		
		for map in res:
			map['map'] = map['map'].split('\n')
			
		return jsonify(result='ok', maps=res, message='All maps')

