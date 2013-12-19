from point import *
import time

MAX_HEALTH = 100
ZERO = point(0, 0)

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

def add_col(collisions, time, val):
	if collisions.has_key(time):
		collisions[time].append(val)
	collisions[time] = [val]		

class player:
	def __init__(self, pid, login, game, server):
		self.pid, self.login, self.game, self.server, self.map = pid, login, game, server, game.map
		self.eps = server.eps

		self.health = MAX_HEALTH
		self.respawn = 1
		
		self.pos = point(0, 0)
		self.speed = point(0, 0)
		self.dv = point(0, 0)

		self.is_start, self.was_action = False, False

		self.connects = []

	#---------------------------function for using on client mess---------------------------------#
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
		self.dv += point(params['dx'],params['dy'])
	#def fire(self, params):

	#----------------------------------function for using on tick---------------------------------#
	def resp(self):
		spawn = self.game.get_spawn()
		self.pos = spawn + point(0.5, 0.5)
		self.speed = point(0,0)
		self.heals = MAX_HEALTH

	def cur_consist(self):
		self.game.pl_mess.append([
			self.pos.x-1,
			self.pos.y-1,
			self.speed.x,
			self.speed.y,
			self.health,
			self.login,
			self.respawn
			])

	def above_floor(self):
		if self.map.is_wall(self.pos + point(.5-self.eps, .5+self.eps)) or\
			self.map.is_wall(self.pos + point(-.5+self.eps, .5+self.eps)):
			return True
		else: return False

	def speed_calc(self):
		if self.above_floor():
			if self.dv.y < -self.eps:
				self.speed.y = -self.game.MAX_SPEED
			if abs(self.dv.x) < self.eps:
				if abs(self.speed.x) < self.game.RUB:
					self.speed.x = 0
				else: 
					self.speed.x -= sign(self.speed.x)*self.game.RUB  
		else:
			self.speed.y += self.game.GRAVITY

		if abs(self.dv.x) > self.eps:
			self.speed.x += sign(self.dv.x)*self.game.ACCEL
		
		if abs(self.speed.x) > self.game.MAX_SPEED:
			self.speed.x = sign(self.speed.x)*self.game.MAX_SPEED
		if abs(self.speed.y) > self.game.MAX_SPEED:
			self.speed.y = sign(self.speed.y)*self.game.MAX_SPEED
		
		self.dv = ZERO

	def take_weapon(self, dot):
		pass

	def take_item(self, dot):
		pass


	def teleport(self, dot):
		self.pos = point(*self.map.tps[dot.to_turple()])
		return

	def peak2peak(self, dist, speed):
		dist_size = dist.size()
		speed_size = speed.size()
		return speed_size > dist_size and\
				(abs(speed.x) < self.eps and abs(dist.x) < self.eps or\
				abs(speed.y) < self.eps and abs(dist.y) < self.eps or\
				(speed.scale(dist_size/speed_size) - dist).size()<self.eps)

	def go(self):
		speed = self.speed
		if speed.size() < self.eps: return
		dir = speed.direct()
		dir1 = point(1 if dir.x else -1, 1 if dir.y else -1)
		#undir = dir.scale(-1,-1)
		center_cell = point(*self.pos.index())
		forward = self.pos + dir1.scale(.5-self.eps)
		forward_cell = point(*forward.index())
		forward = self.pos + dir1.scale(.5)
		
		collisions = {}

		dist = forward_cell + dir - forward
		is_reach_x = abs(speed.x) > abs(dist.x); is_reach_y = abs(speed.y) > abs(dist.y);
		if dist.size() < self.eps:
			add_col(collisions,  dist.size()/speed.size(), (0,3))
		elif self.peak2peak(dist, speed):
			add_col(collisions,  dist.size()/speed.size(), (0,2))
		else:
			if is_reach_x:
				# (a,b)-collision descriptor a(1-center, 0-forward), b(0-x, 1-y, 2-angle)
				add_col(collisions, dist.x/speed.x, (0,0))		
			if is_reach_y:
				add_col(collisions, dist.y/speed.y, (0,1))
				 
		dist = center_cell + dir - self.pos		
		is_reach_x = abs(speed.x) > abs(dist.x); is_reach_y = abs(speed.y) > abs(dist.y);
		if self.peak2peak(dist, self.speed):
			add_col(collisions,  dist.x/speed.x, (1,2))
		else:
			if is_reach_x:
				add_col(collisions, dist.x/speed.x, (1,0))
			if is_reach_y:
				add_col(collisions, dist.y/speed.y, (1,1))

		was_coll = [0,0]
		passed_time = 0
		times = collisions.keys()
		times.sort()
		for time in times:
			for coll in collisions[time]:
				offset = dir1 * point(int(bool(coll[1] - 1)), int(bool(coll[1])))
				if coll[0]:
					if was_coll[0] and coll[1] == 0 or was_coll[1] and coll[0] == 1:
						continue
					coll_cell = center_cell + offset
					if coll[1] == 2:
						coll_cell -= point(*was_coll)*dir1
						 
					el = self.map.map[coll_cell.y][coll_cell.x]
					if '0'<=el<='9': self.teleport(coll_cell); return
					elif 'a'<=el<='Z': self.take_item(coll_item)

				else:				# todo (0,0) collision
					coll_cell = forward_cell + offset
					x_neib_wall = self.map.map[coll_cell.y][coll_cell.x - dir1.x] == '#'
					y_neib_wall = self.map.map[coll_cell.y - dir1.y][coll_cell.x] == '#'
					coll_cell_wall = self.map.map[coll_cell.y][coll_cell.x] == '#'
					if coll[1] == 3:
						if x_neib_wall:
							self.speed.y = 0
							was_coll[1] = 1
						if y_neib_wall:
							self.speed.x = 0
							was_coll[0] = 1
						if abs(self.speed.x) > self.eps and abs(self.speed.y) > self.eps and coll_cell_wall \
							and not y_neib_wall and not x_neib_wall:
							self.speed.y = 0
							was_coll[1] = 1

					elif coll[1] == 2:	  
						if x_neib_wall:
							self.speed.y = 0
							was_coll[1] = 1
						if y_neib_wall:
							self.speed.x = 0
							was_coll[0] = 1
						if abs(self.speed.x) > self.eps and abs(self.speed.y) > self.eps and coll_cell_wall\
							and not y_neib_wall and not x_neib_wall:
							self.speed = point(0,0)
							was_coll = [1,1]

					elif coll[1] == 1:
						if coll_cell_wall or x_neib_wall:
							self.speed.y = 0
							was_coll[1] = 1
					
					elif coll[1] == 0:
						if coll_cell_wall or y_neib_wall:
							self.speed.x = 0
							was_coll[0] = 1

				if was_coll[0] and was_coll[1]: break

		self.pos += speed
		if was_coll[0]:
			self.pos.x = forward_cell.x + .5
		if was_coll[1]:
			self.pos.y = forward_cell.y + .5

	def tick(self):
		if not self.is_start:
			return

		elif self.respawn > 0:
			self.respawn -= 1
			if self.respawn == 0:
				self.resp()

		else:
			t = time.time()
			self.speed_calc()
			self.go()
			print (time.time()-t)*1000
		self.cur_consist()
		return

	def write_mess(self):
		for c in self.connects:
			c.sendMessage(self.game.mess)			