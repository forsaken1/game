from base import *

class GamePreparingTestCase(BaseTestCase):
		
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
				"map": BaseTestCase.defMap,
				"maxPlayers": 8
			})
		assert resp["result"] == "badSid", resp

	def test_createGame_badSid_signInOut(self):
		self.truncate_db()
		sid = self.signin_user()
		resp = self.send("signout",{"sid": sid})
		assert resp["result"] == "ok", resp
		resp = self.send("createGame",
			{
				"sid": sid,
				"name": "RakiSyuda1",
				"map": BaseTestCase.defMap,
				"maxPlayers": 8
			})
		assert resp["result"] == "badSid", resp

	def test_createGame_badName(self):
		resp = self.create_game( is_ret = True, name = 123)
		assert resp["result"] == "badName", resp

	def test_createGame_badMap(self):
		self.truncate_db()
		sid = self.signin_user()
		resp = self.send("createGame",
			{
				"sid": sid,
				"name": "game3",
				"map": BaseTestCase.defMap + 100,
				"maxPlayers": 8
			})
		assert resp["result"] == "badMap", resp

	def test_createGame_badMaxPlayers_str(self):
		resp = self.create_game( is_ret = True, maxPlayers = "badMaxPl")
		assert resp["result"] == "badMaxPlayers", resp

	def test_createGame_badMaxPlayers_moreThenMapMaxPlyaers(self):
		resp = self.create_game( is_ret = True, maxPlayers = 12)
		assert resp["result"] == "badMaxPlayers", resp
		
	def test_createGame_gameExists(self):
		self.create_game()
		resp = self.create_game( is_ret = True, name = self.default('game', 1))
		assert resp["result"] == "gameExists", resp

	def test_createGame_alreadyInGame (self):
		sid = self.signin_user()
		self.join_game(sid = sid)
		resp = self.create_game(is_ret = True, sid = sid)
		assert resp["result"] == "alreadyInGame", resp
		
	def test_getGames_ok(self):
		self.truncate_db()
		self.join_game()
		resp = self.get_game(is_ret = True)
		assert resp.has_key('games'), resp
		games = resp["games"]
		assert len(games) == 2, resp
		for game in games:
			assert game.has_key('id') and type(game['id']) is int, game
			del game['id']
		expect_games = [
			{
				"name": self.default('game', 2),
				"map": BaseTestCase.defMap,
				"maxPlayers": 8,
				"players": [self.default('user', 3), self.default('user', 2)],
				"status": "running"
			},
			{
				"name": self.default('game', 1),
				"map": BaseTestCase.defMap,
				"maxPlayers": 8,
				"players": [self.default('user', 1)],
				"status": "running"
			}
		]
		for game in expect_games:
			assert game in games, [game, games]
		assert resp["result"] == "ok", resp
		
	def test_getGames_badSid(self):
		self.truncate_db()
		sid = self.create_game()
		resp = self.send("getGames",{"sid": sid+"1"})
		assert resp["result"] == "badSid", resp

	def test_joinGame_ok(self):
		self.join_game()

	def test_joinGame_gameFull(self):
		game = self.get_game(maxPlayers = 3)
		for i in range(2):
			self.join_game(game = game)
		sid = self.signin_user()
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game,
			})
		assert resp["result"] == "gameFull", resp

	def test_joinGame_badGame(self):
		self.truncate_db()
		game = self.get_game()
		sid = self.signin_user()		
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game+1
			})
		assert resp["result"] == "badGame", resp
		
	def test_joinGame_alreadyInGame(self):
		sid = self.signin_user()
		game = self.get_game()
		self.join_game(sid = sid)
		resp = self.send("joinGame",
			{
				"sid": sid,
				"game": game,
			})
		assert resp["result"] == "alreadyInGame", resp
		
	
	def test_leaveGame_ok(self):
		game = self.get_game()
		sid = self.join_game( game = game)
		resp = self.send("leaveGame", {"sid": sid})
		assert resp["result"] == "ok", resp

	def test_leaveGame_notInGame_alreadyLeave(self):
		game = self.get_game()
		sid = self.join_game( game = game)
		resp = self.send("leaveGame", {"sid": sid})
		assert resp["result"] == "ok", resp
		resp = self.send("leaveGame", {"sid": sid})
		assert resp["result"] == "notInGame", resp

	def test_leaveGame_notInGame(self):
		game = self.get_game()
		self.join_game(game = game)
		sid = self.signin_user()
		resp = self.send("leaveGame", {"sid": sid})
		assert resp["result"] == "notInGame", resp
	
	def test_last_players_leave_game(self):
		self.truncate_db()
		[game, sid] = self.get_game(sid_returned = True)
		sids = [sid]
		for i in range(2):
			sid = self.signin_user()
			self.join_game(sid = sid, game = game)
			sids.append(sid)
		for sid in sids:
			resp = self.send("leaveGame", {"sid": sid})
			assert resp["result"] == "ok", resp
		resp = self.send("getGames", {"sid": sid})		
		assert resp["result"] == "ok" and resp["games"] == [], resp
		
	def test_signout_from_game(self):
		self.truncate_db()	
		game_resp = self.get_game(is_ret = True)
		game = game_resp['games'][0]['id']
		sid = self.signin_user()
		self.join_game(sid = sid, game = game)
		resp = self.send("signout", {"sid": sid})	
		assert resp["result"] == "ok", resp
		sid = self.signin_user()			
		resp = self.send("getGames", {"sid": sid})
		assert resp == game_resp, [resp, game_resp]