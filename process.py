import MySQLdb, re, os, hashlib, time, json
from projectile import weapons
from config import *
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
	
	def get_pid(self, sid):
		cur = self.db.cursor()
		cur.execute('SELECT id FROM users WHERE sid = %s', (sid,))
		id = cur.fetchone()
		if id: id = id[0]
		else: return None
		return id	
		
	def get_sid(self, pid):
		cur = self.db.cursor()
		cur.execute('SELECT sid FROM users WHERE pid = %s', (sid,))
		id = cur.fetchone()
		if id: id = id[0]
		else: return None
		return id	

	def badSid(self, sid):
		if not self.valid_str(sid): return False
		return self.get_pid(sid)
			

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
		if type(maxPlayers) != int or maxPlayers < 1:
			return False
		else: return True		

	def valid_dot(self, c):										# add new item here
		return c == 'h' or weapons.has_key(c) or '0'<=c<='9' or c=='.' or c=='$' or c=='#' 
	
	def badMap(self, map):
		if type(map) != list or len(map) < 1: return False
		size = len(map[0])
		tp = [0]*10
		for row in map:
			if type(row) != unicode or len(row) != size or not all(self.valid_dot(d) for d in row):
				return False
			for dot in row:
				if '0' <= dot <= '9': tp[int(dot)] +=1
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

class process:		

	def __init__(self, server):
		self.server = server
		server.proc = self
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
			'getGameConsts': ['sid'],
			'getStats':		['sid', 'game']
		}
		cur = self.db.cursor()
		cur.execute('SELECT id, map FROM maps')
		for map in cur.fetchall():
			server.add_map(map[0], map[1].split('\n'))

		cur.execute('SELECT id FROM games WHERE status = 1')
		for game in cur.fetchall():
			cur.execute('DELETE FROM user_game WHERE gid = %s AND kills IS NULL ', (game[0],))			
					
		cur.execute('DELETE FROM games WHERE status = 1')	
		self.db.commit()
			
		
	def __del__(self):
		self.db.close()

	def process(self, req):
		try:
			req = json.loads(req)
			action = req['action']	
			params = req['params']
			if action == 'startTesting':
				return self.start_testing(params)
			act = getattr(self, action)
			formal_param = self.proc_param[action]
			action = act
			error = self.valid.find_error(formal_param, params)
		except ValueError:
			return self.result(error = 'badJSON')
		except (KeyError, TypeError):
			return self.result(error = 'badRequest')
		except AttributeError:
			return self.result(error = 'badAction')
		if error: return self.result(error) 
		else: return action(params)
	
	def is_running_game(self, gid): 
		cur = self.db.cursor()
		cur.execute("SELECT status FROM games WHERE id = %s", (gid,))
		return cur.fetchone()[0]

	def start_testing(self, params):
		if not TESTING:
			return self.result('notInTestMode')
		cursor = self.db.cursor()
		cursor.execute('show tables')
		tables = cursor.fetchall()
		for table in tables:
			cursor.execute('truncate %s' %table)
		self.server.clear(params['websocketMode'])
		return self.result()
		
	def result(self, error = None, param = None):
		result = {"result": "ok", "message": "okey"} if not error else {"result": error, "message": error}
		if param: result = dict(result.items()+param.items())
		return json.dumps(result)
	
	def hash(self, body):
		m = hashlib.sha256()
		m.update(body)
		return m.hexdigest()
	
	def signup(self, par):
		if not (MINLOGIN <= len(par['login']) <= MAXLOGIN) or not all(ord(c) < 128 for c in par['login']):
			return self.result('badLogin')
		if MINLOGIN > len(par['password']) or not all(ord(c) < 128 for c in par['password']):
			return self.result('badPassword')

		cur = self.db.cursor()
		cur.execute('SELECT login FROM users WHERE login = %s', (par['login'],))
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
		id , gid, text = self.valid.get_pid(par['sid']), par['game'], par['text']
		cur = self.db.cursor()

		if gid != "":
			cur.execute('SELECT gid FROM user_game WHERE pid = %s and kills IS NULL', (id,))
			gid_fact = cur.fetchone()
			if not gid_fact or gid_fact[0] != gid:
				return self.result('badGame')
		

		cur.execute('SELECT login FROM users WHERE id = %s', (id,))
		login = cur.fetchone()[0]
		query = 'INSERT INTO messages (login, text, time, gid) VALUES (%s, %s, %s,'+(str(gid) if gid else "NULL")+')'
		cur.execute(query, (login, text, int(time.time())))
		self.db.commit()
		return self.result()
		
	def getMessages(self, par):
		pid, gid, since = self.valid.get_pid(par['sid']), par['game'], int(par['since'])
		
		if gid != "":
			cur = self.db.cursor()
			cur.execute('SELECT gid FROM user_game WHERE pid = %s and kills IS NULL', (pid,))
			gid_fact = cur.fetchone()
			if not gid_fact or gid_fact[0] != gid:
				return self.result('badGame')

		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		query = 'SELECT time, text, login FROM messages WHERE time >= %s AND gid '+('='+str(gid) if gid else "IS NULL")+' ORDER BY time'
		cur.execute(query, (since, ))
		mess = cur.fetchall()
		return self.result(param = {'messages': mess})

	def createGame(self, par):
		sid = par['sid']
		accel, friction, gravity, MaxVelocity = 0.05, 0.05, 0.05, 0.5
		if par.has_key('consts'):
			consts = par['consts']
			accel=consts['accel']; maxVelocity=consts['maxVelocity']; friction=consts['friction']; gravity=consts['gravity']
			if all(0<i<=0.1 for i in (consts['accel'], consts['friction'], consts['gravity'])) and 0<consts['maxVelocity']<1:
				accel, friction, gravity, MaxVelocity = consts['accel'], consts['friction'], consts['gravity'], consts['maxVelocity']
			# add error message for bad game consts

		cur = self.db.cursor()			
		cur.execute('SELECT id FROM games WHERE name = %s', (par['name'],))
		if cur.fetchone():
			return self.result('gameExists')		

		cur.execute('SELECT maxPlayers, id FROM maps WHERE id = %s', (par['map'],))
		mapMax, map = cur.fetchone()
			
		if mapMax < par['maxPlayers']:
			return self.result('badMaxPlayers')
		
		cur = self.db.cursor()
		cur.execute("INSERT INTO games (name, map, maxPlayers, accel, friction, gravity, MaxVelocity)\
			VALUES(%s, %s, %s,%s,%s,%s,%s)", (par['name'], par['map'], par['maxPlayers'], accel, friction, gravity, MaxVelocity))
		self.db.commit()

		gid = cur.lastrowid
		self.server.add_game(map, gid, accel, friction, gravity, MaxVelocity)

		ret = self.joinGame({'sid': sid, 'game': gid})
		if json.loads(ret)['result'] == 'ok':
			return self.result()
		else: 
			cur.execute("DELETE FROM games WHERE name = %s", (par['name'],))
			self.db.commit()		
			return ret
		
	def getGames(self, par):
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		qry = "SELECT id, name, map, maxPlayers, status FROM games "
		if par.has_key('status') and par['status'] in ('running', 'finished'):
			qry += "WHERE status = " + ("1" if par['status'] == 'running' else "0")
		cur.execute(qry)
		res = cur.fetchall()
		for item in res:
			item['status'] = 'running' if item['status'] else 'finished' 
			cur.execute('SELECT login FROM user_game WHERE gid = %i and kills IS NULL ORDER BY id' %item['id'])
			players = cur.fetchall()
			item['players'] = []
			for player in players:
				item['players'].append(player['login'])
		return self.result(param = {'games': res})
		
	def joinGame(self, par):
		pid = self.valid.get_pid(par['sid'])
		gid = par['game']
		if gid == '' or not self.is_running_game(gid):
			return self.result('badGame')

		cur = self.db.cursor()
		cur.execute("SELECT gid FROM user_game WHERE pid = %s AND kills IS NULL", (pid,))
		cur_game = cur.fetchone()
		if cur_game:
			if cur_game[0] == gid:
				return self.result()
			return self.result('alreadyInGame')
			
		cur.execute('SELECT maxPlayers FROM games WHERE id = %s', (gid,))
		maxPlayers = cur.fetchone()[0]
		cur.execute('SELECT count(*) FROM user_game WHERE gid = %s and kills IS NULL', (gid,))
		playersCount = cur.fetchone()[0]
		if playersCount >= maxPlayers:
			return self.result('gameFull')
		
		cur.execute('SELECT login FROM users WHERE id = %s', (pid,))
		login = cur.fetchone()[0]
	
		cur.execute('SELECT kills, deaths FROM user_game WHERE gid = %s and pid = %s', (gid, pid))
		param = cur.fetchone()
		if param:
			(kills, deaths) = param
			cur.execute('UPDATE user_game SET kills = NULL, deaths = NULL WHERE pid = %s and gid = %s', (pid,gid,))
			self.server.add_player(pid, login, gid, kills, deaths)
		else:
			cur.execute('INSERT INTO user_game (pid, login, gid) VALUES(%s, %s, %s)', (pid, login, gid))
			self.server.add_player(pid, login, gid)
		self.db.commit()
		return self.result()
		
	def leaveGame(self, par):		
		pid = self.valid.get_pid(par['sid'])
		cur = self.db.cursor()
		cur.execute("SELECT gid FROM user_game WHERE pid = %s and kills IS NULL", (pid,))
		gid = cur.fetchone()
		if not gid:
			return self.result('notInGame')
		gid = gid[0]			 

		(is_last, kills, deaths) = self.server.erase_player(pid, gid)
		
		cur.execute('UPDATE user_game SET kills = %s, deaths = %s WHERE pid = %s AND gid = %s', (kills, deaths, pid, gid))
		if is_last:
			cur.execute("UPDATE games SET status = 0 WHERE id = %s", (gid,))
		
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

	def getGameConsts(self, par):
		id = self.valid.get_pid(par['sid'])
		cur = self.db.cursor()
		cur.execute('SELECT gid FROM user_game WHERE pid = %s and kills IS NULL', (id,))
		game = cur.fetchone()
		if not game: 
			return self.result('notInGame')
		game = game[0]
		cur.execute('SELECT accel, maxVelocity, gravity, friction FROM games WHERE id = %s', (game,))
		param = {"tickSize": TICK, "accuracy": EPS}
		keys = ('accel', 'maxVelocity', 'gravity', 'friction')
		vals = cur.fetchone()
		for i in range(4):
			param[keys[i]] = vals[i]
		return self.result(param = param)

	def getStats(self, par):
		gid = par['game']
		if gid == '':
			return self.result('badGame')
		if self.is_running_game(gid):
			return self.result('gameRunning')
		cur = self.db.cursor()
		cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT login, kills, deaths FROM user_game WHERE gid = %s", (gid, ))
		return self.result(param = {'players': cur.fetchall()})

	