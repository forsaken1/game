import json
from base import *


def s(t, v = .0, a = ACCEL):
	return v*t + a*(t + t*t)/2.
	
class WebSocketTestCase(BaseTestCase):


	def test_start_ok(self):
		map  = [".........",
				"#$......."]
		ws = self.connect(map)
		resp = self.recv_ws(ws)
		assert resp['projectiles'] == [] and resp['items'] == [], resp
		pl = resp['players'][0]
		assert self.equal(pl[X], 1.5) and self.equal(pl[Y], 1.5) and self.equal(pl[VY], 0)\
			and self.equal(pl[VX], 0), pl
		ws.close()


	def test_first_steps(self):
		map  = [".........",
				"#$......."]
		ws = self.connect(map)
		resp = self.recv_ws(ws)
		pl = resp['players'][0]		
		assert self.equal(pl[X], 1.5) and self.equal(pl[Y], 1.5) and self.equal(pl[VY], 0)\
			and self.equal(pl[VX], 0), pl		

		self.move(ws, resp['tick'], 1, 0)
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[X], 1.5 + s(1.)) and self.equal(pl[Y], 1.5) and self.equal(pl[VY], 0)\
			and self.equal(pl[VX], ACCEL), pl		

		self.move(ws, resp['tick'], 1, -1)
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[X], 1.5 + s(2.)) and self.equal(pl[Y], 1.5 + s(1, a = -MAX_SPEED))\
		    and self.equal(pl[VY], -MAX_SPEED) and self.equal(pl[VX], 2*ACCEL), pl		

	def test_multi_players_with_friction(self):
		map  = [".........",
				".........",
				"#$$......"]
		ws1, game, sid = self.connect(map, game_ret = True)
		resp1 = self.recv_ws(ws1)
		ws2 = self.connect(game = game)
		self.move(ws1, resp1['tick'])
		resp1 = self.recv_ws(ws1)
		resp2 = self.recv_ws(ws2)
		pl1 = resp1['players'][0]
		pl2 = resp2['players'][1]
		assert resp1 == resp2, (resp1, resp2)
		assert self.equal(pl1[X], 1.5) and self.equal(pl1[Y], 2.5) and self.equal(pl1[VY], 0)\
			and self.equal(pl1[VX], 0), pl1
		assert self.equal(pl2[X], 2.5) and self.equal(pl2[Y], 2.5) and self.equal(pl2[VY], 0)\
			and self.equal(pl2[VX], 0), pl2	

		self.move(ws1, resp1['tick'], 1, 0)
		self.move(ws2, resp1['tick'], 1, -1)
		resp1 = self.recv_ws(ws1)
		resp2 = self.recv_ws(ws2)
		pl1 = resp1['players'][0]
		pl2 = resp1['players'][1]
		assert self.equal(pl1[X], 1.5 + s(1.)) and self.equal(pl1[Y], 2.5) and self.equal(pl1[VY], 0)\
			and self.equal(pl1[VX], ACCEL), pl1			
		assert self.equal(pl2[X], 2.5 + s(1.)) and self.equal(pl2[Y], 2.5 + s(1, a = -MAX_SPEED))\
		    and self.equal(pl2[VY], -MAX_SPEED) and self.equal(pl2[VX], ACCEL),\
		    (pl2, 2.5 + s(1.), 	s(1, a = -MAX_SPEED))
		
		self.move(ws1, resp1['tick'])
		self.move(ws2, resp1['tick'])
		resp1 = self.recv_ws(ws1)
		resp2 = self.recv_ws(ws2)
		pl1 = resp1['players'][0]
		pl2 = resp1['players'][1]				
		assert self.equal(pl1[X], 1.5 + s(1.)) and self.equal(pl1[Y], 2.5) and self.equal(pl1[VY], 0)\
			and self.equal(pl1[VX], 0), pl1			
		assert self.equal(pl2[X], 2.5 + s(1.) + s(1,v = ACCEL, a = 0)) and self.equal(pl2[Y],\
		    2.5 + s(1, a = -MAX_SPEED) + s(1, v = -MAX_SPEED ,a = GRAVITY))\
		    and self.equal(pl2[VY], -MAX_SPEED + GRAVITY) and self.equal(pl2[VX], ACCEL), pl2	

	def test_fall(self):
		map = [	"$........",
				"#........",
				"........."]
		ws = self.connect(map)
		resp = self.recv_ws(ws)
		pl = resp['players'][0]		
		assert self.equal(pl[X], 0.5) and self.equal(pl[Y], 0.5) and self.equal(pl[VY], 0)\
			and self.equal(pl[VX], 0), pl			
			
		t = 0
		while(s(t) < 1 - BaseTestCase.accuracy):
			t+=1
			self.move(ws, resp['tick'], 1, 0)
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[Y], 0.5), (pl, t)
						
		self.move(ws, resp['tick'])	
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VY], GRAVITY) and self.equal(pl[Y], 0.5 + s(t = 1, a = GRAVITY)), pl
		
		self.move(ws, resp['tick'])			
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VY], 2*GRAVITY) and self.equal(pl[Y], 0.5 + s(t = 2, a = GRAVITY)), pl		

	def test_teleportation(self):
		map = [	"1........",
				"$........",
				"1........"]	
		ws = self.connect(map)
		s, v = 1.5, 0	
		tps = 0
		while(tps < 2):
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[Y], s) and self.equal(pl[VY], v), (pl, s, v)
			self.move(ws, resp['tick'])
			v += GRAVITY
			if v >= MAX_SPEED: v = MAX_SPEED
			s += v
			if(s >= 2. - BaseTestCase.accuracy):
				s = 0.5; tps+=1				
	
	def test_max_speed(self):
		map = [	"1$.......1"]
		ws = self.connect(map)				
		v = 0
		while v <= MAX_SPEED:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VX], v), (pl, v)
			self.move(ws, resp['tick'], 1)
			v+=ACCEL

		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], MAX_SPEED), (pl, v)

	def test_tp_angle(self):
		map = [	"1.....",
				"$.1..."]
		ws = self.connect(map)	
		resp = self.recv_ws(ws)			
		vy = 0; y = 1.5
		self.move(ws, resp['tick'], 1, -1)
		vy = -MAX_SPEED
		y = 1.5 + vy
		while y > 1:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VY], vy) and self.equal(pl[Y], y) and self.equal(pl[VX], ACCEL), (pl, vy, y)
			self.move(ws, resp['tick'])
			vy+=GRAVITY; y += vy
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], ACCEL) and self.equal(pl[VY], vy)\
		    and self.equal(pl[Y], 1.5) and self.equal(pl[X], 2.5), pl

	def test_players_collision(self):
		map = ["$$"]
		ws1, game, sid = self.connect(map, game_ret = True)
		resp1 = self.recv_ws(ws1)
		ws2 = self.connect(game = game)
		self.move(ws1, resp1['tick'])
		resp1 = self.recv_ws(ws1); resp2 = self.recv_ws(ws2)
		pl1 = resp1['players'][0]; pl2 = resp2['players'][1]
		x1 = 0.5; x2 = 1.5; vx = 0
		while x1 < 1.5:
			vx += ACCEL; x1 += vx; x2 -= vx
			self.move(ws1, resp1['tick'], 1), self.move(ws2, resp1['tick'], -1)
			resp1 = self.recv_ws(ws1); resp2 = self.recv_ws(ws2)

		pl1 = resp1['players'][0]; pl2 = resp2['players'][1]
		assert pl1[X] >=  1.5 and pl2[X] <= 0.5, (pl1, pl2)		###change to equal, when wall collision will done 

	def test_wall(self):
		map = [	"......",
				"$.#..."]
		ws = self.connect(map)	
		resp = self.recv_ws(ws)			
		vx = 0; x = .5
		self.move(ws, resp['tick'], 1)
		vx += ACCEL; x += vx
		while x < 1.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VX], vx) and self.equal(pl[X], x), (pl, vx, x)
			self.move(ws, resp['tick'], 1)
			vx += ACCEL; x += vx 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], 0) and self.equal(pl[VY], 0)\
		    and self.equal(pl[Y], 1.5) and self.equal(pl[X], 1.5), pl			
	
	def test_jump_and_down(self):
		map = [	"......",
				"......",
				"..$..."]
		ws = self.connect(map)	
		resp = self.recv_ws(ws)			
		vy = 0; y = 2.5
		self.move(ws, resp['tick'], 0, -1)
		vy -= MAX_SPEED; y += vy
		while y < 2.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VY], vy) and self.equal(pl[Y], y), (pl, vy, y)
			self.move(ws, resp['tick'])
			vy += GRAVITY; y += vy 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], 0) and self.equal(pl[VY], 0)\
		    and self.equal(pl[Y], 2.5) and self.equal(pl[X], 2.5), pl

	def test_jump_throw_angle(self):
		map = [	"..##..",
				"......",
				"##$###"]
		ws = self.connect(map)	
		resp = self.recv_ws(ws)			
		vy = 0; y = 2.5
		self.move(ws, resp['tick'], 0, -1)
		vy -= MAX_SPEED; y += vy
		while y > 1.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VY], vy) and self.equal(pl[Y], y), (pl, vy, y)
			self.move(ws, resp['tick'], -1)
			vy += GRAVITY; y += vy 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], 0) and self.equal(pl[VY], 0)\
		    and self.equal(pl[Y], 1.5) and self.equal(pl[X], 2.5), pl

		self.move(ws, resp['tick'], -1)
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], -.02) and self.equal(pl[VY], 0)\
		    and self.equal(pl[X], 2.48) and self.equal(pl[Y], 1.5), pl

	def test_peak2peak(self):
		map = [	"..$...",
				"......",
				"....#."]
		ws = self.connect(map)	
		vy = 0; y = .5
		resp = self.recv_ws(ws)			
		self.move(ws, resp['tick'], 1)
		vy += GRAVITY; y += vy
		while y < 1.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VY], vy) and self.equal(pl[Y], y), (pl, vy, y)
			self.move(ws, resp['tick'], 1)
			vy += GRAVITY; y += vy 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], 0) and self.equal(pl[VY], 0)\
		    and self.equal(pl[Y], 1.5) and self.equal(pl[X], 3.5), pl

	def test_take_item(self):
		map = [	"$A..#."]
		ws = self.connect(map)	
		vx = 0; x = .5
		while x < 1:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			it = resp['items']
			assert self.equal(pl[VX], vx) and self.equal(pl[X], x) and it == [0], (pl, vx, x, it)
			self.move(ws, resp['tick'], 1)
			vx += ACCEL; x += vx 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		it = resp['items']
		assert it == [y] and pl[WEAPON] == 'A' and pl[WEAPON_ANGLE] == -1, (it, pl[WEAPON], pl[WEAPON_ANGLE])

	def test_uncommon_consts(self):
		map = [	"$.........."]
		ws = self.connect(map, accel = 0.05, gravity = 0.05, fric = .05, max_speed = 0.5)
		vx = 0; x = .5
		while vx < 0.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VX], vx) and self.equal(pl[X], x), (pl, vx, x)
			self.move(ws, resp['tick'], 1)
			vx += 0.05; x += vx 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[VX], 0.5) , pl

	def test_jump_in_cave(self):
		map = [	"$.....",
				"##..##",
				".....#",
				"....##",]
		ws = self.connect(map)
		vx = 0; x = .5
		while x < 2.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VX], vx) and self.equal(pl[X], x), (pl, vx, x)
			self.move(ws, resp['tick'], 1)
			vx += ACCEL
			if vx > MAX_SPEED: 
				vx = MAX_SPEED
			x += vx 
		vy = 0; y = .5
		while y < 2.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VY], vy) and self.equal(pl[Y], y), (pl, vy, y)
			self.move(ws, resp['tick'], 1)
			vy += ACCEL; 
			if vy > MAX_SPEED: vy = MAX_SPEED;
			y += vy
		vx = ACCEL; x = 3.5 + vx
		while x < 5.5:
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			assert self.equal(pl[VX], vx) and self.equal(pl[X], x), (pl, vx, x)
			self.move(ws, resp['tick'], 1)
			vx += ACCEL; 
			if vx > MAX_SPEED: vx = MAX_SPEED;
			x += vx 
		resp = self.recv_ws(ws)
		pl = resp['players'][0]
		assert self.equal(pl[X], 4.5) and self.equal(pl[Y], 2.5) and self.equal(pl[VX], 0)\
			and self.equal(pl[VY], 0), pl


	def test_leave_game(self):
		map  = [".........",
				".........",
				"#$$......"]
		ws1, game, sid1 = self.connect(map, game_ret = True)
		resp1 = self.recv_ws(ws1)
		ws2 = self.connect(game = game)
		self.move(ws1, resp1['tick'])
		resp1 = self.recv_ws(ws1)
		resp2 = self.recv_ws(ws2)
		pl1 = resp1['players'][0]
		pl2 = resp2['players'][1]
		assert resp1 == resp2, (resp1, resp2)
		assert self.equal(pl1[X], 1.5) and self.equal(pl1[Y], 2.5) and self.equal(pl1[VY], 0)\
			and self.equal(pl1[VX], 0), pl1
		assert self.equal(pl2[X], 2.5) and self.equal(pl2[Y], 2.5) and self.equal(pl2[VY], 0)\
			and self.equal(pl2[VX], 0), pl2	

		ws1.close()
		resp = self.send("leaveGame", {"sid": sid1})
		assert resp["result"] == "ok", resp	
		self.move(ws2, resp1['tick'])
		resp2 = self.recv_ws(ws2)
		assert len(resp2['players']) == 1, resp2['players']
		pl2 = resp2['players'][0]
		assert self.equal(pl2[X], 2.5) and self.equal(pl2[Y], 2.5) and self.equal(pl2[VY], 0)\
			and self.equal(pl2[VX], 0), pl2	

