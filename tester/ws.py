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

	def test_multi_games(self):
		map = self.get_map(scheme = [	"#.............#",
										"#.......$$....#",
										"###############"])
		sid = self.create_game(map = map)			
		ws = self.send_ws('move', {'sid': sid, 'tick': 1, 'dx': 0, 'dy': 0})
		resp = self.recv_ws(ws)
		self.send_ws('move', {'sid': sid, 'tick': 2, 'dx': 1, 'dy': 0}, ws)		
		resp = self.recv_ws(ws)
		resp = self.send("leaveGame", {"sid": sid})
		assert resp["result"] == "ok", resp
		map = self.get_map(scheme = [	"$.",
										"##"])
		sid = self.create_game(map = map)
		ws = self.send_ws('move', {'sid': sid, 'tick': 1, 'dx': 0, 'dy': 0})
		resp = self.recv_ws(ws)		
		assert self.equal(resp['players'][0]['x'], 0.5) and self.equal(resp['players'][0]['y'], 0.5), resp