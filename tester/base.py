import json, unittest, re, MySQLdb, time, requests, sys
from websocket import create_connection
def_map_scheme = [	"#$........#",
					"###########"]


ACCEL, GRAVITY, FRIC, MAX_SPEED = 0.02, 0.02, 0.02, 0.2
X,Y,VX,VY,WEAPON,WEAPON_ANGLE,LOGIN,HEALTH,RESPAWN,KILLS,DEATHS = range(11)

class BaseTestCase(unittest.TestCase):
	HOST, PORT = 'localhost', '5000'
	counter = {'user':0, 'game':0, 'map': 0}
	defMap = 0

	def default(self, item, offset = 0):  
		counter = self.__class__.counter
		if not counter.has_key(item):
			raise AssertionError('not such table:' + item)
		else:
			ret = item + str(counter[item] - offset)
			if not offset: counter[item] += 1
			return ret

	def startTesting(self, sync = True):
		param = {'websocketMode': 'sync' if sync else 'async'}
		resp = self.send('startTesting', param)
		assert resp["result"] == "ok", resp
		BaseTestCase.defMap = self.get_map()				# there's always default map in DB

	def send(self, action = None, params = None, dict = None, wo_dumps = False):
		if dict: 
			query = dict if wo_dumps else json.dumps(dict)
		else: 
			if params is None: query = json.dumps({"action": action})			
			else: query = json.dumps({"action": action, "params": params})
		print query
		resp = requests.post("http://" + self.HOST + ":" + self.PORT, data=query, headers = {"Content-Type": "application/json"})
		print resp.text
		try:
			resp = json.loads(resp.text)
		except:
			assert resp == 0, resp
		assert resp.has_key('result'), resp
		return resp

	def signup_user(self, login = None, passwd = "pass"):
		if login is None: login = self.default('user')
		resp = self.send("signup", {"login": login, "password": passwd })
		assert resp["result"] == "ok", resp

	def signin_user(self, login = None, passwd = "pass"):
		if login is None: login = self.default('user')
		self.signup_user(login, passwd)
		resp = self.send("signin", {"login": login,"password": passwd})
		sid = resp['sid']
		assert resp["result"] == "ok" and resp["sid"] == sid, resp
		return sid

	def send_message(self, sid = None, game = "", text = "some_text"):
		if sid is None: sid = self.signin_user()
		resp = self.send("sendMessage",{"sid": sid,"game": game,"text": text})
		assert resp["result"] == "ok", resp
		return sid
		
	def create_game(self, is_ret = False, sid = None, name = None, map = None, maxPlayers = 8,\
		accel = 0.02, gravity = 0.02, fric = 0.02, max_speed = 0.2):
		if name is None: name = self.default('game')	
		if sid is None: sid = self.signin_user()
		if map is None: map = BaseTestCase.defMap		
		resp = self.send("createGame",
		{
			"sid": sid,
			"name": name,
			"map": map,
			"maxPlayers": maxPlayers,
			"consts": {
			"accel": accel,
			"gravity": gravity,
			"friction": fric,
			"maxVelocity": max_speed}
		})
		if is_ret:
			return resp
		else:		
			assert resp["result"] == "ok", resp	
			return sid

	def join_game(self, game = None, sid = None):
		if game is None: game = self.get_game()	
		if sid is None: sid = self.signin_user()
		resp = self.send("joinGame",
		{
			"sid": sid,
			"game": game,
		})
		assert resp["result"] == "ok", resp
		return sid

	def get_game(self, is_ret = False, maxPlayers = 8, sid_returned = False, map = None,\
			  accel = 0.02, gravity = 0.02, fric = 0.02, max_speed = 0.2, status  = 0):				# unsorted massive bug
		sid = self.signin_user()

		if status:	resp = self.send("getGames", {"sid": sid, "status": status})
		else:		resp = self.send("getGames", {"sid": sid})
		old_games = resp['games']		
		name = self.default('game')
		if map is None: map = self.defMap
		sid = self.create_game(name = name, map = map, maxPlayers = maxPlayers,\
			accel = accel, gravity = gravity, fric = fric, max_speed = max_speed)
		resp = self.send("getGames", {"sid": sid})
		if is_ret: return resp
		assert resp.has_key('games'), resp
		games = resp['games']
		for og in old_games:
			if og in games: games.remove(og)
		game = games[0]
		assert game.has_key('id') and type(game['id']) is int, game
		id = game["id"]
		del game["id"]
		assert resp["result"] == "ok" and game == {
			"name": name,
			"map": map,
			"maxPlayers": maxPlayers,
			"players": [self.default('user', 1)],
			"status": "running"
		}, [game, map, name, self.default('user', 1)]

		if sid_returned: return [id, sid]
		return id

	def upload_map(self, map = def_map_scheme, is_ret = False, name = None, maxPlayers = 8, sid = None):
		if name is None: name = self.default('map')
		if sid is None: sid = self.signin_user()
		resp = self.send("uploadMap",
		{
			'sid': sid,
			'name': name,
			'map': map,
			'maxPlayers': maxPlayers
		})
		if is_ret: return resp
		assert resp["result"] == "ok", resp
		return sid

	def get_map(self, is_ret = False, sid = None, maxPlayers = 8, scheme = ["#$........#","###########"]):# unsorted massive bug
		if sid is None: sid = self.signin_user()	
		self.upload_map(maxPlayers = maxPlayers, map = scheme)
		
		resp = self.send("getMaps",{'sid': sid})
		if is_ret: return resp
		assert resp.has_key('maps'), resp
		maps = resp['maps']
		maps[:-1] = []
		map = maps[0]
		assert map.has_key('id') and type(map['id']) is int, map
		id = map["id"]
		del map["id"]
		assert resp["result"] == "ok" and resp["maps"] == [
		{
			"name": self.default('map', 1),
			"map": scheme,
			"maxPlayers": maxPlayers,
		}], resp
		return id	



#-----------------------------------webSocket utils----------------------------------------#
	def take_gun(self, ws, limit = 1, dir = 1):
		resp = {}
		resp['tick'] = self.tick
		while True:
			self.move(ws, resp['tick'], dir)
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			if pl[X]*dir > limit*dir: return pl[X]

	def fire(self, ws, x, y=0, tick = None):
		if tick is None:
			tick = self.tick
		self.send_ws('fire', {'tick': tick, 'dx': x, 'dy': y}, ws)

	def equal(self, x, y):
		return abs(x-y) < BaseTestCase.accuracy

	def send_ws(self, action = None, params = None, ws = None):
		if ws is None: 
			ws = create_connection("ws://" + self.HOST + ":" + self.PORT + "/websocket")
		mess = json.dumps({'action': action,'params': params})
		print '-----', mess
		ws.send(mess)
		return ws

	def recv_ws(self, ws):
		mess = json.loads(ws.recv())
		self.tick = mess['tick']
		print '+++++', mess
		return mess

	def connect(self, map = None, game = None, game_ret = False,\
			  accel = 0.02, gravity = 0.02, fric = 0.02, max_speed = 0.2):
		if map:
			map = self.get_map(scheme = map)
			gid, sid = self.get_game(map = map, sid_returned = True,\
			accel = accel, gravity = gravity, fric = fric, max_speed = max_speed)
			ws = self.send_ws(action = 'move', params = {'sid': sid, 'tick': 0, 'dx': 0, 'dy':0})
			if game_ret:
				return ws, gid, sid
			return ws
		elif game:
			sid = self.join_game(game)
			ws = self.send_ws(action = 'move', params = {'sid': sid, 'tick': 0, 'dx': 0, 'dy':0})
			if game_ret:
				return ws, sid
			return ws
		else: return False

	def move(self, ws, tick = None, x = 0, y = 0):
		if tick is None:
			tick = self.tick
		if not x and not y:		self.send_ws('empty', {'tick': tick}, ws)
		else:					self.send_ws('move', {'tick': tick, 'dx': x, 'dy': y}, ws)
			

class game:
	def __init__(self, test, map = ["#######", ".......", "$P....."], add_players_count = 0, \
			  accel = 0.02, gravity = 0.02, fric = 0.02, max_speed = 0.2):
		self.pl_count = add_players_count + 1
		self.was_action = [False]*(self.pl_count)
		self.connections = []
		self.sids = []
		self.test = test
		ws, game, sid = test.connect(map, game_ret = True, accel = accel, gravity = gravity, fric = fric, max_speed = max_speed)
		self.connections.append(ws)
		self.sids.append(sid)
		self.resp = test.recv_ws(ws)
		for i in range(add_players_count):
			ws, sid = test.connect(game = game, game_ret = True)
			self.connections.append(ws), self.sids.append(sid)
			self.resp = test.recv_ws(ws)
			
	def tick(self):
		for i in range(self.pl_count):
			if not self.was_action[i]: 
				self.test.send_ws(action = 'move', params = {'sid': self.sids[i], 'tick': 0, 'dx': 0, 'dy':0}, ws = self.connections[i])
			else: self.was_action[i] = False

		for i in range(self.pl_count):
			resp = self.test.recv_ws(self.connections[i])
		return resp


	def move(self, pl, x = 0, y = 0):
		if self.was_action[pl]:
			raise Exception("second msg from player during one tick")
		self.test.move(self.connections[pl], x = x, y = y)
		self.was_action[pl] = True

	def fire(self, pl = 0, x = 0, y = 0):
		if self.was_action[pl]:
			raise Exception("second msg from player during one tick")
		self.test.fire(self.connections[pl], x = x, y = y)
		self.was_action[pl] = True