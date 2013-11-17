import json, unittest, re, MySQLdb, time, requests, sys

def_map_scheme = [	"#$........#",
					"###########"]


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
		resp = requests.post("http://" + self.HOST + ":" + self.PORT, data=query, headers = {"Content-Type": "application/json"})
		try:
			resp = json.loads(resp.text)
		except:
			assert resp == 0, resp
		assert resp.has_key('result'), resp
		print resp
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
		assert re.match('^\w+$', sid), sid
		assert resp["result"] == "ok" and resp["sid"] == sid, resp
		return sid

	def send_message(self, sid = None, game = "", text = "some_text"):
		if sid is None: sid = self.signin_user()
		resp = self.send("sendMessage",{"sid": sid,"game": game,"text": text})
		assert resp["result"] == "ok", resp
		return sid
		
	def create_game(self, is_ret = False, sid = None, name = None, map = None, maxPlayers = 8):	#add map id
		if name is None: name = self.default('game')	
		if sid is None: sid = self.signin_user()
		if map is None: map = BaseTestCase.defMap		
		resp = self.send("createGame",
		{
			"sid": sid,
			"name": name,
			"map": map,
			"maxPlayers": maxPlayers
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

	def get_game(self, is_ret = False, maxPlayers = 8, sid_returned = False, map = None):				# unsorted massive bug
		sid = self.signin_user()
		resp = self.send("getGames", {"sid": sid})
		old_games = resp['games']		
		name = self.default('game')
		if map is None: map = self.get_map()
		sid = self.create_game(name = name, map = map, maxPlayers = maxPlayers)
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
		}, [resp, map, name, self.default('user', 1)]

		if sid_returned: return [id, sid]
		return id

	def upload_map(self, map = [def_map_scheme], is_ret = False, name = None, maxPlayers = 8, sid = None):
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
		maps[:-1] = [] #bug!
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