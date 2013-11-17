from websocket import create_connection
import json
from base import *

class WebSocketTestCase(BaseTestCase):

	def equal(self, x, y):
		return abs(x-y) < BaseTestCase.accuracy

	def send_ws(self, action = None, params = None, ws = None):
		if ws is None: ws = create_connection("ws://" + self.HOST + ":" + self.PORT + "/websocket")
		ws.send(json.dumps({
			'action': action,
			'params': params
		}))
		return ws

	def recv_ws(self, ws):
		return json.loads(ws.recv())

	def test_wall_coll(self):
		map = self.get_map(scheme = [	"#....#........#",
										"#....$........#",
										"###############"])
		sid = self.create_game(map = map)
		ws = self.send_ws('move', {'sid': sid, 'tick': 0, 'dx': 0, 'dy': 0})
		resp = self.recv_ws(ws)
		pl1 = resp['players'][0]
		assert self.equal(pl1['x'], 5.5) and self.equal(pl1['y'], 1.5) \
			and self.equal(pl1['vx'], 0) and self.equal(pl1['vy'], 0), pl1

		self.send_ws('move', {'sid': sid, 'tick': resp['tick'], 'dx': 0, 'dy': -1}, ws)
		resp = self.recv_ws(ws)
		pl1 = resp['players'][0]
		assert self.equal(pl1['x'], 5.5) and self.equal(pl1['y'], 1.5) \
			and self.equal(pl1['vx'], 0) and self.equal(pl1['vy'], 0), pl1
		

