from sympy.geometry import *

MAX_HEALTH = 100
MAX_SPEED = 1
ZERO = Point(0, 0)
TICK = 30

class player:
	def __init__(self, sid, login, game):
		self.sid = sid
		self.game = game
		
		self.health = MAX_HEALTH
		self.status = 0
		self.respawn = -1

		self.pos = Point(0, 0)
		self.speed = Point(0, 0)
		self.is_start = False

		self.connects = []
		self.was_action = False

	def action(self, msg):
		self.was_action = True
		if msg['action'] != 'empty':
			getattr(self, msg['action'])(msg['params'])
		self.game.sync_tick()

	def move(self, params):
		# add tick handler
		print params, self.game.ticks
		if not self.is_start:
			self.is_start = True
			return
		dv = Point(params['dx'],params['dy'])
		if dv.y != 0:
			#if self.on_floor
			self.speed = Point(self.speed.x, -MAX_SPEED)
		self.speed += Point(dv.x/dv.distance(ZERO), 0)			#zero div bug
		if self.speed.x > MAX_SPEED:
			self.speed = Point(MAX_SPEED, self.speed.y)
		elif self.speed.x < -MAX_SPEED:
			self.speed = Point(-MAX_SPEED, self.speed.y)

	#def fire(self, params):

	def resp(self):
		self.pos = self.game.get_spawn() + Point(0.5, 0.5)
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

	def tick(self):
		if not self.is_start:
			return

		elif self.status == 0:
			self.respawn -= TICK
			if self.respawn <= 0:
				self.resp()

		else:
			if self.speed.x > 0.1:
				self.speed -= Point(0.1,0)
			elif self.speed.x < -0.1:
				self.speed += Point(0.1,0)
			else :
				self.speed = Point(0, self.speed.y)
			self.pos += self.speed
		self.cur_consist()
		return

	def write_mess(self):
		for c in self.connects:
			c.sendMessage(self.game.mess)