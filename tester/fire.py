from base import *
from point import *

class FireTestCase(BaseTestCase):


	def test_simple_knife_fire(self):
		map  = ["$........"]
		ws = self.connect(map)
		resp = self.recv_ws(ws)
		assert resp['projectiles'] == [] and resp['items'] == [], resp

		self.fire(ws, 3)
		resp = self.recv_ws(ws)		
		
		assert len(resp['projectiles']) == 1, resp['projectiles']
		pr = resp['projectiles'][0]
		assert self.equal(pr[X],0.5) and self.equal(pr[Y],0.5) and \
			self.equal(pr[VX], weapons['K'].speed) and self.equal(pr[VY], 0) and pr[WEAPON] == 'K', pr

		self.move(ws, resp['tick'])
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		assert self.equal(pr[VX], 0) and self.equal(pr[VY], 0) and pr[WEAPON] == 'K', pr

		self.move(ws, resp['tick'])
		resp = self.recv_ws(ws)
		assert resp['projectiles'] == [], resp['projectiles']


	def test_pistol(self):
		map  = ["$P..."]
		ws = self.connect(map)
		self.recv_ws(ws)		
		x = self.take_gun(ws)
		self.fire(ws, 3)
		y = .5
		vx = weapons['P'].speed; vy = 0
		while x + vx< 5:
			resp = self.recv_ws(ws)
			pr = resp['projectiles'][0]
			assert self.equal(pr[X], x) and self.equal(pr[Y], y) and self.equal(pr[VX], vx) and self.equal(pr[VY], vy), pr 
			print x
			x+=vx
			self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		assert self.equal(pr[X], x) and self.equal(pr[Y], y) and self.equal(pr[VX], 5-x) and self.equal(pr[VY], vy), pr
		self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		assert self.equal(pr[X], 5) and self.equal(pr[Y], y) and self.equal(pr[VX], 0) and self.equal(pr[VY], 0), pr 
		#right vertical test needed


	def test_pistol_by_angle(self):
		map  = ["#######",
				".......",
				"$P....."]
		ws = self.connect(map)
		self.recv_ws(ws)		
		x = self.take_gun(ws)
		y = 2.5
		self.fire(ws,1,-1)
		vx = weapons['P'].speed/sqrt(2)
		vy = -weapons['P'].speed/sqrt(2)
		while y+vy>1:
			resp = self.recv_ws(ws)
			pr = resp['projectiles'][0]
			assert self.equal(pr[X], x) and self.equal(pr[Y], y) and self.equal(pr[VX], vx) and self.equal(pr[VY], vy), (pr, vx,vy)  
			x+=vx
			y+=vy
			self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		vy1 = vy
		vy = 1-y
		vx = vx*vy/vy1
		assert self.equal(pr[X], x) and self.equal(pr[Y], y) and self.equal(pr[VX], vx) and self.equal(pr[VY], vy), (pr, vx,vy) 
		x+=vx
		self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		assert self.equal(pr[X], x) and self.equal(pr[Y], 1) and self.equal(pr[VX], 0) and self.equal(pr[VY], 0), (pr, vx,vy) 


	def test_pistol_right_up(self):
		map  = ["#######",
				".......",
				"$P....."]
		ws = self.connect(map)
		self.recv_ws(ws)		
		x = self.take_gun(ws)
		y = 2.5
		self.fire(ws,0,-1)
		vy = -weapons['P'].speed
		vx = 0
		while y+vy>1:
			resp = self.recv_ws(ws)
			pr = resp['projectiles'][0]
			assert self.equal(pr[Y], y) and self.equal(pr[VY], vy), (pr, vy)  
			y+=vy
			self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		vy = 1-y
		assert self.equal(pr[Y], y) and self.equal(pr[VY], vy), (pr, vy) 
		self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		assert self.equal(pr[Y], 1) and self.equal(pr[VX], 0) and self.equal(pr[VY], 0), (pr, vx,vy)

	def test_rails(self):
		map  = ["....A$",
				"##...#",
				"##...."]
		ws = self.connect(map)
		resp = self.recv_ws(ws)		
		while True:
			self.move(ws, resp['tick'], -1)
			resp = self.recv_ws(ws)
			pl = resp['players'][0]
			if pl[X] < 5: break
		x = pl[X]
		y = .5
		self.fire(ws, 2-x, 1-y)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		vy = 1-y
		vx = 2-x
		assert self.equal(pr[X], x) and self.equal(pr[Y], y) and self.equal(pr[VX], vx) and self.equal(pr[VY], vy), (pr, vx,vy)  
		self.move(ws)
		resp = self.recv_ws(ws)
		pr = resp['projectiles'][0]
		assert self.equal(pr[X], 2) and self.equal(pr[Y], 1) and self.equal(pr[VX], 0) and self.equal(pr[VY], 0), (pr, vx,vy)

	def test_machinegun_recharge(self):
		map  = ["$M...................................."]
		ws = self.connect(map)
		self.recv_ws(ws)		
		x = self.take_gun(ws)
		for i in range(0, weapons['M'].recharge):
			self.fire(ws, 3)
			prs = self.recv_ws(ws)['projectiles']
			assert len(prs) == 1, (prs, i)
		self.fire(ws, 3)
		prs = self.recv_ws(ws)['projectiles']
		assert len(prs) == 2,(prs,i)
					

	def test_machinegun_hitting(self):
		map  = ["$......",
				"#......",
				"$M#...."]
		ws1, game, sid = self.connect(map, game_ret = True)
		resp = self.recv_ws(ws1)
		ws2 = self.connect(game = game)
		self.move(ws1, resp['tick'])
		resp = self.recv_ws(ws1)
		self.recv_ws(ws2)

		while True:
			self.move(ws2, resp['tick'], 1)
			self.move(ws1)
			resp = self.recv_ws(ws1)
			self.recv_ws(ws2)
			pl = resp['players'][1]
			if self.equal(pl[X], 1.5): break

		x = 1.5
		v = point(1-1.5, .5-2.5)
		w = weapons['M']
		v = v.scale(w.speed/v.size())
		while x +v.x> 1:
			self.fire(ws2, v.x, v.y)
			self.move(ws1)
			resp = self.recv_ws(ws1)
			self.recv_ws(ws2)
			x += v.x		

		health = 100
		i = 0
		while health > 0:
			assert resp['players'][0][HEALTH] == health, (pl, health)
			self.fire(ws2, v.x,v.y)
			self.move(ws1)
			resp = self.recv_ws(ws1)
			self.recv_ws(ws2)
			if (not i%w.recharge): health -= w.damage
			i += 1
		pl = resp['players'][0]
		assert pl[HEALTH] == 0 and pl[RESPAWN] == RESP_PLAYER  and pl[DEATHS] == 1, pl
		pl = resp['players'][1]
		assert pl[KILLS] == 1, pl

	def test_rocket_launcher(self):
		map  = ["$R..$."]
		ws1, game, sid = self.connect(map, game_ret = True)
		resp = self.recv_ws(ws1)
		ws2 = self.connect(game = game)
		self.move(ws1, resp['tick'])
		resp = self.recv_ws(ws1)
		self.recv_ws(ws2)		

		while True:
			self.move(ws1, x = 1)
			self.move(ws2)
			resp = self.recv_ws(ws1)
			self.recv_ws(ws2)
			pl = resp['players'][0]
			if pl[X] > 1: break
		self.fire(ws1,2)
		x = pl[X]
		while x < 5:
			self.move(ws2)
			self.move(ws1)
			resp = self.recv_ws(ws1)
			self.recv_ws(ws2)
			x += weapons['R'].speed
		pl = resp['players'][1]
		assert pl[HEALTH] == 100 - weapons['R'].damage and pl[VX] == MAX_SPEED, pl

		


