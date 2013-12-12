from sympy.geometry import *
import time

MAX_HEALTH = 100
ZERO = Point(0, 0)

def sign(x):
	return 1 if x > 0 else -1

def all_types_wo_wall():
	types = ''
	i = ord('0')
	while chr(i) < '9':
		i+=1
		types += chr(i)
	i = ord('a')
	while chr(i) < 'z':
		i+=1
		types += chr(i)
	i = ord('A')
	while chr(i) < 'Z':
		i+=1
		types += chr(i)
	return types

types = all_types_wo_wall()

def direct(vect):
	return Point(int(vect.x>=0), int(vect.y>=0))

def point2turple(p):
	return (p.x, p.y)

def norm(vect):
	return vect/(vect.distance(ZERO))

def cell_index(a):
	return (int(a.x), int(a.y))

def add_col(collisions, time, val):
	if collisions.has_key(time):
		cillision[time].append(val)
	collisions[time] = [val]		

class player:
	def __init__(self, pid, login, game, server):
		self.pid, self.login, self.game, self.server, self.map = pid, login, game, server, game.map
		self.eps = server.eps

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
		if self.map.is_wall(self.pos.translate(-0.5 + self.eps, 0.5 + self.eps)) or\
			self.map.is_wall(self.pos.translate(0.5 - self.eps, 0.5 + self.eps)):
			return True
		else: return False

	def speed_calc(self):
		if self.above_floor():
			if self.dv.y < -self.eps:
				self.speed = Point(self.speed.x, -self.game.MAX_SPEED)
			if abs(self.dv.x) < self.eps:
				if abs(self.speed.x) < self.game.RUB:
					self.speed = Point(0, self.speed.y)
				else:
					self.speed -= Point(sign(self.speed.x)*self.game.RUB, 0)
		else:
			self.speed += Point(0, self.game.GRAVITY)

		if abs(self.dv.x) > self.eps:
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


	def teleport(self, dot):
		self.pos = self.map.tps[dot]
		return

	def peak2peak(self, dist, speed):
		dist_size = dist.distance(ZERO)
		speed_size = speed.distance(ZERO)
		return speed_size > dist_size and\
				(dist_size < self.eps or\
				abs(speed.x) < self.eps and abs(dist.x) < self.eps or\
				abs(speed.y) < self.eps and abs(dist.y) < self.eps or\
				(speed.scale(dist_size/speed_size, dist_size/speed_size) - dist).distance(ZERO)<self.eps)

	def go(self):
		if self.speed.distance(ZERO) < self.eps: return
		dir = direct(self.speed)
		dir1 = Point(1 if dir.x else -1, 1 if dir.y else -1)
		#undir = dir.scale(-1,-1)
		center_cell = Point(*cell_index(self.pos))
		forward = self.pos + dir1.scale(.5-self.eps, .5-self.eps)
		forward_cell = Point(*cell_index(forward))
		
		collisions = {}

		dist = forward_cell+dir-forward-dir1.scale(self.eps, self.eps) 
		is_reach_x = abs(self.speed.x) > abs(dist.x); is_reach_y = abs(self.speed.y) > abs(dist.y);
		if self.peak2peak(dist, self.speed):
			add_col(collisions,  dist.x/self.speed.x, (0,2))
		else:
			if is_reach_x:
				add_col(collisions, dist.x/self.speed.x, (0,0))						# (a,b)-collision description a(1-center, 0-forward), b(0-x, 1-y, 2-angle)
			if is_reach_y:
				add_col(collisions, dist.y/self.speed.y, (0,1))
				 
		dist = center_cell + dir - self.pos		
		is_reach_x = abs(self.speed.x) > abs(dist.x); is_reach_y = abs(self.speed.y) > abs(dist.y);
		if self.peak2peak(dist, self.speed):
			add_col(collisions,  dist.x/self.speed.x, (1,2))
		else:
			if is_reach_x:
				add_col(collisions, dist.x/self.speed.x, (1,0)) 
			if is_reach_y:
				add_col(collisions, dist.y/self.speed.y, (1,1)) 

		passed_time = 0
		for time in collisions.keys():
			for coll in collisions[time]:

				offset = dir1.scale(int(bool(coll[1] - 1)), int(bool(coll[1])))
				if coll[0]:
					coll_cell = center_cell + offset
					el = self.map.el_by_point(coll_cell)
					if '0'<=el<='9': self.teleport(coll_cell); return
					elif 'a'<=el<='z': self.take_item(coll_item)
					elif 'A'<=el<='Z': self.take_weapon(coll_item)

				else:				# todo (0,0) collision
					null_x = abs(self.speed.x) < self.eps; null_y = abs(self.speed.y) < self.eps
					if coll[1] == 2 and (null_x or null_y):
						if self.map.is_wall(forward_cell + offset.scale(null_y, null_x)):
							self.pos += self.speed*(time - passed_time)
							self.speed = ZERO
							return
						break
					coll_cell = forward_cell + offset

					if self.map.is_wall(coll_cell):
						if time < self.eps and coll[1] == 2 and dir.y == 1:
							self.speed.scale(1, 0)
							break
						self.pos += self.speed*(time - passed_time)
						passed_time = time
						self.speed = self.speed.scale(int(not offset.x), int(not offset.y))
						return
						# trace += cur dot
					else:
						if offset.x:					# add multi intersection proofer if maxVel > 0.5
							neighbor = coll_cell.translate(0, -offset.y)
							if abs(self.speed.y) > self.eps and self.map.is_wall(neighbor):
								self.pos += self.speed*(time - passed_time)
								passed_time = time
								self.speed = Point(0, self.speed.y)
						if offset.y:
							neighbor = coll_cell.translate(-offset.x, 0)
							if abs(self.speed.x) > self.eps and self.map.is_wall(coll_cell):
								self.pos += self.speed*(time - passed_time)
								passed_time = time
								self.speed = Point(self.speed.x, 0)
		self.pos += self.speed.scale(1-passed_time, 1-passed_time)


	def tick(self):
		if not self.is_start:
			return

		elif self.status == 0:
			self.respawn -= self.server.tick_size
			if self.respawn <= 0:
				self.resp()

		else:
			#t = time.time()
			self.speed_calc()
			#print (time.time()-t)*1000
			self.go()
		self.cur_consist()
		return

	def write_mess(self):
		for c in self.connects:
			c.sendMessage(self.game.mess)			