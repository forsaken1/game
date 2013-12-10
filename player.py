from sympy.geometry import *

MAX_HEALTH = 100
ZERO = Point(0, 0)

def sign(x):
	return 1 if x > 0 else -1

class player:
	def __init__(self, pid, login, game, server):
		self.pid, self.login, self.game, self.server, self.map = pid, login, game, server, game.map
		
		self.health = MAX_HEALTH
		self.status = 0
		self.respawn = -1

		self.pos, self.speed, self.dv = ZERO, ZERO, ZERO
		self.is_start, self.was_action = False, False

		self.connects = []

	#----------------------------------function for using on client mess---------------------------------#
	def action(self, msg):
		if not self.is_start:
			self.is_start = True
			self.was_action = True
			self.game.sync_tick()
			return

		if self.game.c_ticks - 1 <= msg['params']['tick'] <= self.game.c_ticks: 
			self.was_action = True
			if msg['action'] != 'empty':
				getattr(self, msg['action'])(msg['params'])
			self.game.sync_tick()

	def move(self, params):
		self.dv += Point(params['dx'],params['dy'])
	#def fire(self, params):

	#----------------------------------function for using on tick---------------------------------#
	def resp(self):
		spawn = self.game.get_spawn()
		self.pos = spawn + Point(0.5, 0.5)
		self.speed = ZERO
		self.status = 1
		self.heals = MAX_HEALTH

	def cur_consist(self):
		self.game.pl_mess.append({
			'x': float(self.pos.x)-1,
			'y': float(self.pos.y)-1,
			'vx': float(self.speed.x),
			'vy': float(self.speed.y),
			'health': self.health,
			'status': 'alive' if self.status else 'dead',
			'respawn': self.respawn
			})

	def above_floor(self):
		if self.map.is_wall(self.pos.translate(-0.5 + self.server.eps, 0.5 + self.server.eps)) or\
			self.map.is_wall(self.pos.translate(0.5 - self.server.eps, 0.5 + self.server.eps)):
			return True
		else: return False

	def speed_calc(self):
		if self.above_floor():
			if self.dv.y < -self.server.eps:
				self.speed = Point(self.speed.x, -self.game.MAX_SPEED)
			if abs(self.dv.x) < self.server.eps:
				if abs(self.speed.x) < self.game.RUB:
					self.speed = Point(0, self.speed.y)
				else:
					self.speed -= Point(sign(self.speed.x)*self.game.RUB, 0)
		else:
			self.speed += Point(0, self.game.GRAVITY)

		if abs(self.dv.x) > self.server.eps:
			self.speed += Point(sign(self.dv.x)*self.game.ACCEL, 0)
		
		if abs(self.speed.x) > self.game.MAX_SPEED:
			self.speed = Point(sign(self.speed.x)*self.game.MAX_SPEED, self.speed.y)
		if abs(self.speed.y) > self.game.MAX_SPEED:
			self.speed = Point(self.speed.x, sign(self.speed.y)*self.game.MAX_SPEED)
		
		self.dv = ZERO

	def take_weapon(self, dot):
		pass

	def take_item(self, dot):
		pass

	def at_wall(self, dist, dot):
		return False
		self.pos += self.speed/self.speed.distance(ZERO)*dist
		if self.server.equal(dot['pt'].x, dot['sq'].x) and self.speed.x > 0 or \
		self.server.equal(dot['pt'].x, dot['sq'].x + 1) or self.speed.x < 0:
			self.speed = Point(0, self.speed.y)
			return True

		elif self.server.equal(dot['pt'].y, dot['sq'].y) and self.speed.y > 0 or \
			self.server.equal(dot['pt'].y, dot['sq'].y + 1) and self.speed.y < 0:
			self.speed = Point(self.speed.x, 0)
			return True

		else: return False	

	def teleport(self, dot):
		if self.server.equal(dot['sq'].x, int(self.pos.x)) and self.server.equal(dot['sq'].y, int(self.pos.y)):
			return False
		self.pos = self.map.tps[dot['sq']]
		return True

	def go(self):
		if self.speed == ZERO: return
		end = self.pos + self.speed
		collision = {}
		for i in (-0.5, 0.5):
			for j in (-0.5, 0.5):
				collision.update(self.map.collision_detect(self.pos.translate(i,j), end.translate(i,j), '#'))
		collision.update(self.map.collision_detect(self.pos, end))

		for dist, dots in collision.iteritems():
			for dot in dots:
				type = dot['tp']
				if 'A' <= type <= 'Z':		self.take_weapon(dot)
				elif 'a' <= type <= 'z':	self.take_item(dot)
				elif type == '#':			
					if self.at_wall(dist, dot): return
				elif '1' <= type <= '9':	
					if self.teleport(dot): return

		self.pos = end


	def tick(self):
		if not self.is_start:
			return

		elif self.status == 0:
			self.respawn -= self.server.tick_size
			if self.respawn <= 0:
				self.resp()

		else:
			self.speed_calc()
			self.go()

		self.cur_consist()
		return

	def write_mess(self):
		for c in self.connects:
			c.sendMessage(self.game.mess)