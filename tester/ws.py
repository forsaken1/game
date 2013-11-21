from websocket import create_connection
import json
from base import *

ACCEL, GRAVITY, RUB, MAX_SPEED = 0.02, 0.02, 0.02, 0.2	

def s(t, v = .0, a = ACCEL):
	return v*t + a*(t + t*t)/2.
	
class WebSocketTestCase(BaseTestCase):

	

	def equal(self, x, y):
		return abs(x-y) < BaseTestCase.accuracy

	def send_ws(self, action = None, params = None, ws = None):
		if ws is None: ws = create_connection("ws://" + self.HOST + ":" + self.PORT + "/websocket")
		mess = json.dumps({'action': action,'params': params})
		print '-----', mess
		ws.send(mess)
		return ws

	def recv_ws(self, ws):
		mess = json.loads(ws.recv())
		print '+++++', mess
		return mess

	def test_start_ok(self):
		map = self.get_map(scheme = [	".........",
										"#$......."])
		sid = self.create_game(map = map)
		ws = self.send_ws(action = 'move', params = {'sid': sid, 'tick': 0, 'dx': 0, 'dy':0})
		resp = self.recv_ws(ws)
		assert resp['projectiles'] == [] and resp['items'] == [], resp
		pl = resp['players'][0]
		assert self.equal(pl['x'], 1.5) and self.equal(pl['y'], 1.5) and self.equal(pl['vy'], 0)\
			and self.equal(pl['vx'], 0), pl

	#def test_async_mode(self):
	#	self.startTesting(False)
	#	sid = self.create_game()
	#	ws = self.send_ws(action = 'move', params = {'sid': sid, 'tick': 0, 'dx': 0, 'dy':0})
	#	time.sleep(0.5)
	#	for i in range(10):
	#		self.recv_ws(ws)
	#	resp = self.recv_ws(ws)
	#	self.startTesting(True)
	#	assert resp['tick'] >= 10, resp

	#def test_first_steps(self):
	#	map = self.get_map(scheme = [	".........",
	#									"#$......."])
	#	sid = self.create_game(map = map)
	#	ws = self.send_ws('move', {'sid': sid, 'tick': 0, 'dx': 0, 'dy': 0})
	#	resp = self.recv_ws(ws)
	#	pl = resp['players'][0]		
	#	assert self.equal(pl['x'], 1.5) and self.equal(pl['y'], 1.5) and self.equal(pl['vy'], 0)\
	#		and self.equal(pl['vx'], 0), pl		

	#	self.send_ws('move', {'sid': sid, 'tick': resp['tick'], 'dx': 1, 'dy': 0}, ws)
	#	resp = self.recv_ws(ws)
	#	pl = resp['players'][0]
	#	assert self.equal(pl['x'], 1.5 + s(1.)) and self.equal(pl['y'], 1.5) and self.equal(pl['vy'], 0)\
	#		and self.equal(pl['vx'], ACCEL), pl		

	#	self.send_ws('move', {'sid': sid, 'tick': resp['tick'], 'dx': 1, 'dy': -1}, ws)
	#	resp = self.recv_ws(ws)
	#	pl = resp['players'][0]
	#	assert self.equal(pl['x'], 1.5 + s(2.)) and self.equal(pl['y'], 1.5 + s(1, a = -MAX_SPEED))\
	#	    and self.equal(pl['vy'], -MAX_SPEED) and self.equal(pl['vx'], 2*ACCEL), pl		

	#def test_multi_players_with_rub(self):
	#	map = self.get_map(scheme = [	".........",
	#									".........",
	#									"#$$......"])
	#	sid2 = self.signin_user()
	#	gid, sid1 = self.get_game(map = map, sid_returned = True)
	#	self.join_game(gid, sid2)
	#	ws1 = self.send_ws('move', {'sid': sid1, 'tick': 0, 'dx': 0, 'dy': 0})
	#	ws2 = self.send_ws('move', {'sid': sid2, 'tick': 0, 'dx': 0, 'dy': 0})
	#	mess1 = self.recv_ws(ws1)
	#	mess2 = self.recv_ws(ws2)
	#	pl1 = mess1['players'][0]
	#	pl2 = mess1['players'][1]
	#	assert mess1 == mess2, (mess1, mess2)
	#	assert self.equal(pl1['x'], 1.5) and self.equal(pl1['y'], 2.5) and self.equal(pl1['vy'], 0)\
	#		and self.equal(pl1['vx'], 0), pl1
	#	assert self.equal(pl2['x'], 2.5) and self.equal(pl2['y'], 2.5) and self.equal(pl2['vy'], 0)\
	#		and self.equal(pl2['vx'], 0), pl2	

	#	self.send_ws('move', {'sid': sid1, 'tick': mess1['tick'], 'dx': 1, 'dy': 0}, ws1)
	#	self.send_ws('move', {'sid': sid2, 'tick': mess1['tick'], 'dx': 1, 'dy': -1}, ws2)
	#	mess1 = self.recv_ws(ws1)
	#	mess2 = self.recv_ws(ws2)
	#	pl1 = mess1['players'][0]
	#	pl2 = mess1['players'][1]
	#	assert self.equal(pl1['x'], 1.5 + s(1.)) and self.equal(pl1['y'], 2.5) and self.equal(pl1['vy'], 0)\
	#		and self.equal(pl1['vx'], ACCEL), pl1			
	#	assert self.equal(pl2['x'], 2.5 + s(1.)) and self.equal(pl2['y'], 2.5 + s(1, a = -MAX_SPEED))\
	#	    and self.equal(pl2['vy'], -MAX_SPEED) and self.equal(pl2['vx'], ACCEL), (pl2, 2.5 + s(1.), 	s(1, a = -MAX_SPEED))
		
	#	self.send_ws('empty', {'tick': mess1['tick']}, ws1)
	#	self.send_ws('empty', {'tick': mess1['tick']}, ws2)
	#	mess1 = self.recv_ws(ws1)
	#	mess2 = self.recv_ws(ws2)
	#	pl1 = mess1['players'][0]
	#	pl2 = mess1['players'][1]				
	#	assert self.equal(pl1['x'], 1.5 + s(1.)) and self.equal(pl1['y'], 2.5) and self.equal(pl1['vy'], 0)\
	#		and self.equal(pl1['vx'], 0), pl1			
	#	assert self.equal(pl2['x'], 2.5 + s(1.) + s(1,v = ACCEL, a = 0)) and self.equal(pl2['y'],\
	#	    2.5 + s(1, a = -MAX_SPEED) + s(1, v = -MAX_SPEED ,a = GRAVITY))\
	#	    and self.equal(pl2['vy'], -MAX_SPEED + GRAVITY) and self.equal(pl2['vx'], ACCEL), pl2	

	def test_fall(self):
		map = self.get_map(scheme = [	"$........",
										"#........",
										"........."])		
		sid = self.create_game(map = map)
		ws = self.send_ws('move', {'sid': sid, 'tick': 0, 'dx': 0, 'dy': 0})
		resp = self.recv_ws(ws)
		pl = resp['players'][0]		
		assert self.equal(pl['x'], 0.5) and self.equal(pl['y'], 0.5) and self.equal(pl['vy'], 0)\
			and self.equal(pl['vx'], 0), pl			
			
		t = 0
		while(s(t) < 1 + BaseTestCase.accuracy):
			t+=1
			self.send_ws('move', {'sid': sid, 'tick': resp['tick'], 'dx': 1, 'dy': 0}, ws)
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl['y'], 0.5), (pl, t)
						
		self.send_ws('empty', {'tick': resp['tick']}, ws)		
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl['vy'], GRAVITY) and self.equal(pl['y'], 0.5 + s(t = 1, a = GRAVITY)), pl
		
		self.send_ws('empty', {'tick': resp['tick']}, ws)		
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl['vy'], 2*GRAVITY) and self.equal(pl['y'], 0.5 + s(t = 2, a = GRAVITY)), pl		
		
	#def test_wall_coll(self):
	#	map = self.get_map(scheme = [	"#....#........#",
	#									"#....$........#",
	#									"###############"])
	#	sid = self.create_game(map = map)
	#	ws = self.send_ws('move', {'sid': sid, 'tick': 0, 'dx': 0, 'dy': 0})
	#	resp = self.recv_ws(ws)
	#	pl1 = resp['players'][0]
	#	assert self.equal(pl1['x'], 5.5) and self.equal(pl1['y'], 1.5) \
	#		and self.equal(pl1['vx'], 0) and self.equal(pl1['vy'], 0), pl1

	#	self.send_ws('move', {'sid': sid, 'tick': resp['tick'], 'dx': 0, 'dy': -1}, ws)
	#	resp = self.recv_ws(ws)
	#	pl1 = resp['players'][0]
	#	assert self.equal(pl1['x'], 5.5) and self.equal(pl1['y'], 1.5) \
	#		and self.equal(pl1['vx'], 0) and self.equal(pl1['vy'], 0), pl1