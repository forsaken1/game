from sympy.geometry import *

MAX_HEALTH = 100
MAX_SPEED = 1
ZERO = Point(0, 0)

class player:
	def __init__(self, sid, login, game, server):
		self.sid, self.game, self.login, self.server = sid, login, game, server
		
		self.health = MAX_HEALTH
		self.status = 0
		self.respawn = -1

		self.pos = self.speed = Point(0, 0)
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

	def speed_calc(self):
		if self.speed.x > 0.1:
			self.speed -= Point(0.1,0)
		elif self.speed.x < -0.1:
			self.speed += Point(0.1,0)
		else :
			self.speed = Point(0, self.speed.y)

	def take_weapon(self, dot):
		pass

	def take_item(self, dot):
		pass

	def at_wall(self, dot):


	def go(self):
		end = self.pos + self.speed
		collision = {}
		for i in (-0.5, 0.5):
			for j in (-0.5, 0.5):
				collision.update(self.game.map.collision_detect(self.pos.translate(i,j), end.translate(i,j), '#'))
		collision.update(self.game.map.collision_detect(self.pos, end))

		for dist, dot in collision.iteritems():
			type = dot[2]
			if 'A' <= type <= 'Z': self.take_weapon(dot)
			elif 'a' <= type <= 'z': self.take_item(dot)
			elif type == '#': 
				self.at_wall(dot); return
			elif '1' <= type <= '9': 
				if self.teleport(dot): return


	def tick(self):
		if not self.is_start:
			return

		elif self.status == 0:
			self.respawn -= TICK
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