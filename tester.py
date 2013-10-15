# -*- coding: utf-8 -*-

from run import app
import json, unittest, re, MySQLdb, time, process, requests
from websocket import create_connection

host, port = 'localhost', '5000'
counter = {'user':0, 'game':0}	
test = True

def default(item, offset = 0):  
	if not counter.has_key(item):
		raise AssertionError('not such table:' + item)
	else:
		ret = item + str(counter[item] - offset)
		if not offset: counter[item] += 1
		return ret
		
class MyTestCase(unittest.TestCase):
	def truncate_db(self):
		counter = {'user':0, 'game':0}	
		query = json.dumps({"action": "startTesting"})
		if test:
			resp = self.app.post('/', data=query)
			resp = json.loads(resp.data)		
		else:
			resp = requests.post("http:/" + host + ":" + port, data=query)
			resp = json.loads(resp.text)	
		assert resp == {"result": "ok"}, resp
		
	def setUp(self):
		app.config["TESTING"] = True
		self.app = app.test_client()
		self.truncate_db()

	def send(self, action, params):
		query = json.dumps(
		{
			"action": action,
			"params": params
		})
	
		if test:
			resp = self.app.post('/', data=query)
			resp = json.loads(resp.data)		
		else:
			resp = requests.post("http:/" + host + ":" + port, data=query)
			resp = json.loads(resp.text)
		if resp.has_key('message'):
			del resp['message']
		return resp

	def signup_user(self, login = 0, passwd = "pass"):
		if not login: login = default('user')
		resp = self.send("signup", {"login": login, "password": passwd })
		assert resp == {"result": "ok"}, resp

	def signin_user(self, login = 0, passwd = "pass"):
		if not login: login = default('user')
		self.signup_user(login, passwd)
		resp = self.send("signin", {"login": login,"password": passwd})
		sid = resp['sid']
		assert re.match('^\w+$', sid), sid
		assert resp == {"result": "ok", "sid": sid}, resp
		return sid

	def send_message(self, game = "", text = "some_text"):
		sid = self.signin_user()
		resp = self.send("sendMessage",{"sid": sid,"game": game,"text": text})
		assert resp == {"result": "ok"}, resp
		return sid
		
	def create_game(self, is_ret = False, sid = 0, name = 0, map = "map", maxPlayers = 8):	#add map id
		if not name: name = default('game')	
		if not sid: sid = self.signin_user()
	
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
			assert resp == {"result": "ok"}, resp	
			return sid
		
		
	def join_game(self, game = 0, sid = 0):
		if not game: game = self.get_game()	
		if not sid: sid = self.signin_user()
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game,
			})
		assert resp == {"result": "ok"}, resp
		return sid

	def get_game(self, is_ret = False, name = 0, map = "map", maxPlayers = 8):
		if not name: name = default('game')
		sid = self.create_game(name = name, map = map, maxPlayers = maxPlayers)
		resp = self.send("getGames", {"sid": sid})
		if is_ret: return resp
		assert resp.has_key('games'), resp
		games = resp['games']
		for i in range(len(games)-1):
			del games[i]
		game = games[0]
		assert game.has_key('id') and type(game['id']) is int, game
		id = game["id"]
		del game["id"]
		assert resp == {"result": "ok", "games": [
		{
			"name": name,
			"map": map,
			"maxPlayers": maxPlayers,
			"players": [default('user', 1)],
			"status": "running"
		}]}, [resp, name, default('user', 1)]
		return id
			
class AuthTestCase(MyTestCase):
	
	def test_startTesting(self):
		self.truncate_db()
	
	def test_unknown_action_not_action(self):
		query = json.dumps(
		{
			"params":
			{
				"login": "user",
				"password": "pass"
			}
		})
		resp = self.app.post('/', data=query)
		resp = json.loads(resp.data)
		if resp.has_key('message'):
			del resp['message']
		assert resp == { "result": "unknownAction" }, resp

	def test_unknown_action_isnot_json(self):
		resp = json.loads(self.app.post('/', data="fooooooo").data)
		if resp.has_key('message'):
			del resp['message']
		assert resp == { "result": "unknownAction" }, resp

	def test_unknown_action(self):
		resp = self.send("unknown_action", {"login": "userr","password": "pass" })
		if resp.has_key('message'):
			del resp['message']
		assert resp == { "result": "unknownAction" }, resp

	def test_signup_ok(self):
		self.signup_user()

	def test_signup_bad_pass(self):
		resp = self.send("signup",{"login": default('user'),"password": "p"})
		assert resp == { "result": "badPassword" }, resp

	def test_signup_bad_tooshort(self):
		resp = self.send("signup",{"login": "u","password": "pass3"})
		assert resp == { "result": "badLogin" }, resp

	def test_signup_bad_toolong(self):
		resp = self.send("signup",{"login": "ThisStringConsistMoreThen40LattersNeedSomeMore", "password": "pass3"})
		assert resp == { "result": "badLogin" }, resp
		
	def test_signup_bad_unicode(self):
		resp = self.send("signup",{"login": u"паруски", "password": "pass3"})
		assert resp == { "result": "badLogin" }, resp
		
	def test_signup_already_exists(self):
		self.signup_user()
		resp = self.send("signup", {"login": default('user', 1), "password": "pass"})
		assert resp == { "result": "userExists" }, resp

	def test_signin_ok(self):
		self.signin_user()

	def test_signin_bad_combi(self):
		self.signup_user()
		resp = self.send("signin",{"login": default('user', 1), "password": "bad_pass"})
		assert resp == { "result": "incorrect" }, resp

	def test_signout_ok(self):
		sid = self.signin_user()
		resp = self.send("signout", {"sid": sid})
		assert resp == {"result": "ok"}, resp

	def test_signout_bad_sid(self):
		self.truncate_db()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("signout", {"sid": sid1 + sid2})
		assert resp == {"result": "badSid"}, resp

class ChatTestCase(MyTestCase):

	def test_sendMessage_ok(self):
		self.send_message()

	def test_sendMessage_ok_cyr(self):
		self.send_message( text = (u"привет == hello".encode('utf-8')))

	def test_sendMessage_ok_from_game(self):
		id = self.get_game()
		self.send_message(game = id, text = "***")		
	
	def test_sendMessage_badSid(self):
		self.truncate_db()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("sendMessage", {"sid": sid1 + sid2,"game": "","text": "hello"})
		assert resp == {"result": "badSid"}, resp

	def test_sendMessage_badGame(self):
		self.truncate_db()
		sid = self.signin_user()		
		resp = self.send("sendMessage", {"sid": sid,"game": 1111,"text": "hello"})	
		assert resp == {"result": "badGame"}

	def test_getMessages_ok(self):
		self.send_message(text = "0th")
		time.sleep(5)
		timestamp1 = int(time.time())
		sid1 = self.send_message(text = "1st")
		time.sleep(5)
		timestamp2 = int(time.time())
		sid2 =self.send_message(text = "2nd")
		resp = self.send("getMessages",
			{
				"sid": sid1,
				"game": "",
				"since": timestamp1
			})
		assert resp.has_key('messages'), resp
		mess = resp['messages']
		assert mess[0]['time'] < mess[1]['time']		
		del resp['messages'][0]['time']
		del resp['messages'][1]['time']
		assert resp == {"result": "ok", "messages": [
			{
				"text": "1st",
				"login": default('user', 2)
			},
			{
				"text": "2nd",
				"login": default('user', 1)
			}]}, resp
	
	def test_getMessages_from_game_ok(self):
		id1 = self.get_game()
		id2 = self.get_game()
		self.send_message(text = "0th", game = id1)
		time.sleep(5)
		timestamp1 = int(time.time())
		sid1 =self.send_message(text = "1st", game = id1)
		time.sleep(5)
		sid2 =self.send_message(text = "2nd", game = id2)
		time.sleep(5)
		sid3 =self.send_message(text = "3rd", game = id1)	
		resp = self.send("getMessages",
			{
				"sid": sid1,
				"game": id1,
				"since": timestamp1
			})
		assert resp.has_key('messages'), resp			
		mess = resp['messages']
		assert mess[0]['time'] < mess[1]['time']		
		del resp['messages'][0]['time']
		del resp['messages'][1]['time']
		assert resp == {"result": "ok", "messages": [
			{
				"text": "1st",
				"login": default('user', 3)
			},
			{
				"text": "3rd",
				"login": default('user', 1)
			}]}, resp
			
	def test_getMessages_badSid(self):
		self.truncate_db()    
		timestamp = int(time.time())
		sid1 =self.send_message()
		sid2 =self.send_message()
		resp = self.send("getMessages",
			{
				"sid": sid1 + sid2,
				"game": "",
				"since": timestamp
			})
		assert resp == {"result": "badSid"}, resp

	def test_getMessages_badSince_stirng(self):
		timestamp = int(time.time())
		sid =self.send_message()
		resp = self.send("getMessages",
			{
				"sid": sid,
				"game": "",
				"since": "badTimestamp"
			})
		assert resp == {"result": "badSince"}, resp

class GamePreparingTestCase(MyTestCase):
		
	def test_createGame_ok(self):
		self.create_game()

	def test_createGame_badSid(self):
		self.truncate_db()
		sid1 = self.signin_user()
		sid2 = self.signin_user()
		resp = self.send("createGame",
			{
				"sid": sid1 + sid2,
				"name": "RakiSyuda",
				"map": "bestMap",
				"maxPlayers": 8
			})
		assert resp == {"result": "badSid"}, resp

	def test_createGame_badSid_signInOut(self):
		self.truncate_db()
		sid = self.signin_user()
		resp = self.send("signout",{"sid": sid})
		assert resp == {"result": "ok"}, resp
		resp = self.send("createGame",
			{
				"sid": sid,
				"name": "RakiSyuda1",
				"map": "bestMap",
				"maxPlayers": 8
			})
		assert resp == {"result": "badSid"}, resp

	def test_createGame_badName(self):
		resp = self.create_game( is_ret = True, name = "***")
		assert resp == {"result": "badName"}, resp

	def test_createGame_badMap(self):
		sid = self.signin_user()
		resp = self.send("createGame",
			{
				"sid": sid,
				"name": "game3",
				"map": "notInBase",                # there isn't such map in DB
				"maxPlayers": 8
			})
		assert resp == {"result": "ok"}, resp      #   "result": "badMap"

	def test_createGame_badMaxPlayers(self):
		resp = self.create_game( is_ret = True, maxPlayers = "badMaxPl")
		assert resp == {"result": "badMaxPlayers"}, resp

	def test_createGame_gameExists(self):
		self.create_game()
		resp = self.create_game( is_ret = True, name = default('game', 1))
		assert resp == {"result": "gameExists"}, resp

	def test_createGame_alreadyInGame (self):
		sid = self.signin_user()
		self.join_game(sid = sid)
		resp = self.create_game(is_ret = True, sid = sid)
		assert resp == {"result": "alreadyInGame"}, resp
		
	def test_getGames_ok(self):
		self.truncate_db()
		self.join_game()
		resp = self.get_game( is_ret = True)
		assert resp.has_key('games'), resp
		games = [
			{
				"name": default('game', 2),
				"map": "map",
				"maxPlayers": 8,
				"players": [default('user', 3), default('user', 2)],
				"status": "running"
			},
			{
				"name": default('game', 1),
				"map": "map",
				"maxPlayers": 8,
				"players": [default('user', 1)],
				"status": "running"
			}
		]
		for game in resp["games"]:
			assert game.has_key('id') and type(game['id']) is int, game
			del game['id']
		for game in games:		
			assert resp["games"].count(game) == 1, resp
		del resp["games"]
		assert resp == {"result":"ok"}, resp
		
	def test_getGames_badSid(self):
		self.truncate_db()
		sid = self.create_game()
		resp = self.send("getGames",{"sid": sid+"1"})
		assert resp == {"result": "badSid"}, resp

	def test_joinGame_ok(self):
		self.join_game()

	def test_joinGame_gameFull(self):
		game = self.get_game(maxPlayers = 3)
		for i in range(2):
			self.join_game( game = game)
		sid = self.signin_user()
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game,
			})
		assert resp == {"result": "gameFull"}, resp

	def test_joinGame_badGame(self):
		self.truncate_db()
		game = self.get_game()
		sid = self.signin_user()		
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game+1
			})
		assert resp == {"result": "badGame"}, resp
		
	def test_joinGame_alreadyInGame(self):
		sid = self.signin_user()
		game = self.create_game()
		self.join_game(sid = sid)
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game,
			})
		assert resp == {"result": "alreadyInGame"}, resp
		
	
	def test_leaveGame_ok(self):
		game = self.get_game()
		sid = self.join_game( game = game)
		resp = self.send("leaveGame", {"sid": sid})
		assert resp == {"result": "ok"}, resp

	def test_leaveGame_notInGame_alreadyLeave(self):
		game = self.get_game()
		sid = self.join_game( game = game)
		resp = self.send("leaveGame", {"sid": sid})
		assert resp == {"result": "ok"}, resp
		resp = self.send("leaveGame", {"sid": sid})
		assert resp == {"result": "notInGame"}, resp

	def test_leaveGame_notInGame(self):
		game = self.get_game()
		self.join_game( game = game)
		sid = self.signin_user()
		resp = self.send("leaveGame", {"sid": sid})
		assert resp == {"result": "notInGame"}, resp

class WSTestCase(unittest.TestCase):
	def setUp(self):
		self.ws = create_connection('ws://' + host + ':' + port + '/webSocket')

	def test_ws(self):
		self.ws.send('1001')
		resp = self.ws.recv()
		assert resp == '1011', resp
		
if __name__ == '__main__':
   log_file = 'log.txt'
   f = open(log_file, "w")
   runner = unittest.TextTestRunner(f)
   unittest.main(testRunner=runner)
   f.close()