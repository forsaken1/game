import MySQLdb, re, os, hashlib, time, json

MINLOGIN, MAXLOGIN = 4, 40
LONGBLOB = 65535

class param_validator:
	def valid_str(self, str, min = 1, max = 255):
		if type(str) == unicode and min <= len(str) <= max and all(ord(c) < 128 for c in str):
			return True
		else: return False	
		
	def badLogin(self, login):
		return type(login) == unicode
		
	def badPassword(self, password):
		return type(password) == unicode
		
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
		tp = [0]*10
		for row in map:
			if type(row) != unicode or len(row) != size or not all(self.valid_dot(d) for d in row):
				for dot in row:
					if '0' <= dot <= '9': tp[int(dot)] +=1
				return False
		for t in tp:
			if t != 2 and t != 0:
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

	def __init__(self, server):
		self.server = server
		db_name = 'game'
		self.db = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd='', db=db_name)
		self.valid = param_validator(self.db)
		self.proc_param = {
			'signup': 		['login', 'password'],
			'signin': 		['login', 'password'],
			'signout': 		['sid'],
			'sendMessage': 	['sid', 'game', 'text'],
			'getMessages': 	['sid', 'game', 'since'],
			'createGame': 	['sid', 'name', 'mapId', 'maxPlayers'],
			'getGames': 	['sid'],
			'joinGame': 	['sid', 'game'],
			'leaveGame': 	['sid'],
			'uploadMap': 	['sid', 'name', 'map', 'maxPlayers'],
			'getMaps': 		['sid'],
		}		
		
	def __del__(self):
		self.db.close()

	def process(self, req):
		try:
			req = json.loads(req)
			action = req['action']	
			print action
			if action == 'startTesting':
				return self.start_testing()
			params = req['params']
			act = getattr(self, action)
			formal_param = self.proc_param[action]
			action = act
			error = self.valid.find_error(formal_param, params)
		except ValueError:
			return self.result(error = 'badJSON')
		except KeyError:
			return self.result(error = 'badRequest')
		except AttributeError:
			return self.result(error = 'unknownAction')
		if error: return self.result(error) 
		else: return action(params)
	
	def start_testing(self):
		data = open("conf", "r").read()
		if (self.config()['testing'] != 'yes'):
			return self.result('notInTestMode')
		cursor = self.db.cursor()
		cursor.execute('show tables')
		tables = cursor.fetchall()
		for table in tables:
			cursor.execute('truncate %s' %table)

		self.server.clear()

		return self.result()
		
	def result(self, error = None, param = None):
		result = {"result": "ok", "message": "okey"} if not error else {"result": error, "message": "error"}
		if param: result = dict(result.items()+param.items())
		return json.dumps(result)
	
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
	
	def signup(self, par):
		if not (MINLOGIN <= len(par['login']) <= MAXLOGIN) or not all(ord(c) < 128 for c in par['login']):
			return self.result('badLogin')
		if MINLOGIN > len(par['password']) or not all(ord(c) < 128 for c in par['password']):
			return self.result('badPassword')

		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE login = %s', (par['login'],))		# change db lib, use query param
		if cur.fetchone():
			return self.result('userExists')
		
		cur.execute('INSERT INTO users (login, password) VALUES (%s, %s)', (par['login'], self.hash(par['password']),))
		self.db.commit()
		return self.result()
	
	def signin(self, par):
		cur = self.db.cursor()
		cur.execute('SELECT id FROM users WHERE login = %s AND password = %s', (par['login'], self.hash(par['password']),))
		res = cur.fetchone()
		if not res:
			return self.result('incorrect')
		
		ssid = self.hash(os.urandom(32) + 'key' + self.hash(os.urandom(32)))
		cur.execute("UPDATE users SET sid = %s WHERE id = %s", (ssid,res[0],))
		self.db.commit()
		return self.result(param = {'sid': ssid})
		
	def signout(self, par):
		sid = par['sid']
		self.leaveGame({'sid': sid})
		
		self.db.cursor().execute('UPDATE users SET sid = NULL WHERE sid = %s', (sid,))
		self.db.commit()
		return self.result()
		
	def sendMessage(self, par):
		sid , gid, text = par['sid'], par['game'], par['text']
		cur = self.db.cursor()

		cur.execute('SELECT game_id FROM user_game WHERE sid = %s', (sid,))
		gid_fact = cur.fetchone()
		gid_fact = gid_fact[0] if gid_fact else ""
		if gid_fact != gid:
			return self.result('badGame')

		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))
		login = cur.fetchone()[0]
		query = 'INSERT INTO messages (login, text, time, game_id) VALUES (%s, %s, %s,'+(str(gid) if gid else "NULL")+')'
		cur.execute(query, (login, text, int(time.time())))
		self.db.commit()
		return self.result()
		
	def getMessages(self, par):
		gid, since = par['game'], par['since']
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		query = 'SELECT time, text, login FROM messages WHERE time >= %s AND game_id '+('='+str(gid) if gid else "IS NULL")+' ORDER BY time'
		cur.execute(query, (since, ))
		mess = cur.fetchall()
		return self.result(param = {'messages': mess})
		
	def createGame(self, par):
		sid = par['sid']
			
		cur = self.db.cursor()			
		cur.execute('SELECT id FROM games WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return self.result('gameExists')		

		cur.execute('SELECT maxPlayers, id FROM maps WHERE id = %s', (par['map'],))
		mapMax, map = cur.fetchone()
			
		if mapMax < par['maxPlayers']:
			return self.result('badMaxPlayers')
		
		cur = self.db.cursor()
		cur.execute("INSERT INTO games (name, map, maxPlayers) VALUES(%s, %s, %s)", (par['name'], par['map'], par['maxPlayers']))
		self.db.commit()

		gid = cur.lastrowid
		self.server.add_game(map, gid)

		ret = self.joinGame({'sid': sid, 'game': gid})
		if json.loads(ret)['result'] == 'ok':
			return self.result()				
		else: 
			cur.execute("DELETE FROM games WHERE name = %s", (par['name'],))
			self.db.commit()		
			return ret
		
	def getGames(self, par):
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
		return self.result(param = {'games': res})
		
	def joinGame(self, par):
		sid = par['sid']	
		gid = par['game']
		cur = self.db.cursor()
		if par['game'] == "":
			return self.result('badGame')
		cur.execute('SELECT id FROM user_game WHERE sid = %s', (sid,))
		if cur.fetchone():
			return self.result('alreadyInGame')					
			
		cur.execute('SELECT maxPlayers FROM games WHERE id = %s', (gid,))
		maxPlayers = cur.fetchone()[0]
		cur.execute('SELECT count(*) FROM user_game WHERE game_id = %s', (gid,))
		playersCount = cur.fetchone()[0]
		if playersCount >= maxPlayers:
			return self.result('gameFull')
			
		cur.execute('SELECT login FROM users WHERE sid = %s', (sid,))	
		login = cur.fetchone()[0]
		cur.execute('INSERT INTO user_game (sid, login, game_id) VALUES(%s, %s, %s)', (sid, login, gid))
		self.db.commit()

		self.server.add_player(sid, login, gid)

		return self.result()
		
	def leaveGame(self, par):		
		sid = par['sid']
		cur = self.db.cursor()
		cur.execute('SELECT game_id FROM user_game WHERE sid = %s', (sid,))
		game = cur.fetchone()
		if not game: 
			return self.result('notInGame')
		game = game[0]			
		
		cur.execute('DELETE from user_game WHERE sid = %s', (sid, ))
		self.db.commit()
		
		self.server.erase_player(sid, game)

		cur.execute('SELECT count(*) FROM user_game WHERE game_id = %s', (game,))
		if not cur.fetchone()[0]:
			cur.execute('DELETE from games WHERE id = %s', (game,))			
		self.db.commit()
		return self.result()
		
	def uploadMap(self, par):			
		cur = self.db.cursor()
		cur.execute('SELECT id FROM maps WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return self.result('mapExists')
		strmap = ''
		for row in par['map']:
			strmap += row + '\n'
		strmap = strmap[:-1]
		cur.execute("INSERT INTO maps (name, map, maxPlayers) VALUES(%s, %s, %s)",
					(par['name'], strmap, par['maxPlayers']))

		self.db.commit()
		mid = cur.lastrowid
		self.server.add_map(mid, par['map'])
		return self.result()

	def getMaps(self, par):			
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT id, name, map, maxPlayers FROM maps')	
		res = cur.fetchall()
		for map in res:
			map['map'] = map['map'].split('\n')
			
		return self.result(param = {'maps': res})

