from websocket import create_connection
import json
from base import *

class WebSocketTestCase(BaseTestCase):
	EPS = 1e-6

	def equal(self, x, y):
		return abs(x-y) < self.EPS

	def send_ws(self, action = None, params = None, ws = None):
		if ws is None: ws = create_connection("ws://" + self.HOST + ":" + self.PORT + "/websocket")
		ws.send(json.dumps({
			'action': action,
			'params': params
		}))
		return ws

	def recv_ws(self, ws):
		return json.loads(ws.recv())

	def test_move_ok(self):
		sid = self.create_game()
		ws = self.send_ws(action = 'move', params = {'sid': sid, 'tick': 0, 'dx': 0, 'dy':0})
		resp = self.recv_ws(ws)
		assert resp['tick'] == 1 and resp['projectiles'] == [] and resp['items'] == [], resp
		pl = resp['players'][0]
		assert self.equal(pl['x'], 1.5) and self.equal(pl['y'], 0.5) and self.equal(pl['vy'], 0) and self.equal(pl['vx'], 0), pl

	def test_async_mode(self):
		self.startTesting(False)
		sid = self.create_game()
		ws = self.send_ws(action = 'move', params = {'sid': sid, 'tick': 0, 'dx': 0, 'dy':0})
		time.sleep(0.5)
		for i in range(10):
			self.recv_ws(ws)
		resp = self.recv_ws(ws)
		self.startTesting(True)
		assert resp['tick'] >= 10, resp


	def test_first_steps(self):
		map = self.get_map(scheme = [	"#.............#",
										"#$............#",
										"###############"])
		sid = self.create_game(map = map)
		ws = self.send_ws('move', {'sid': sid, 'tick': 0, 'dx': 0, 'dy': 0})
		resp = self.recv_ws(ws)
		pl1 = resp['players'][0]
		
		self.send_ws('move', {'sid': sid, 'tick': resp['tick'] + 1, 'dx': 1, 'dy': 0}, ws)
		resp = self.recv_ws(ws)
		pl2 = resp['players'][0]
		assert pl1['x'] < pl2['x'] and self.equal(pl1['y'], pl2['y']) and pl2['vx'] > 0 and self.equal(pl2['vy'], 0), [pl1, pl2]

		self.send_ws('move', {'sid': sid, 'tick': resp['tick'] + 1, 'dx': 1, 'dy': -1}, ws)
		resp = self.recv_ws(ws)
		pl3 = resp['players'][0]
		assert pl2['x'] < pl3['x'] and pl2['y'] > pl3['y'] and pl3['vx'] > 0 and pl3['vy'] < 0, [pl3, pl2]

	def test_multi_players(self):
		map = self.get_map(scheme = [	"#.............#",
										"#.......$$....#",
										"###############"])
		sid2 = self.signin_user()
		gid, sid1 = self.get_game(map = map, sid_returned = True)
		self.join_game(gid, sid2)
		ws1 = self.send_ws('move', {'sid': sid1, 'tick': 0, 'dx': 0, 'dy': 0})
		ws2 = self.send_ws('move', {'sid': sid2, 'tick': 0, 'dx': 0, 'dy': 0})
		mess1 = self.recv_ws(ws1)
		mess2 = self.recv_ws(ws2)
		assert mess1 == mess2, (mess1, mess2)

		self.send_ws('move', {'sid': sid1, 'tick': 0, 'dx': -1, 'dy': 0}, ws1)
		self.send_ws('move', {'sid': sid2, 'tick': 0, 'dx': 0, 'dy': -1}, ws2)
		mess1 = self.recv_ws(ws1)
		mess2 = self.recv_ws(ws2)
		
		pl1 = mess1['players'][0]
		pl2 = mess1['players'][1]
		assert pl1['vx'] < pl2['vx'] and pl1['x'] < pl2['x'], (pl1, pl2)
		assert pl1['vy'] > pl2['vy'] and pl1['y'] > pl2['y'], (pl1, pl2)		
		
