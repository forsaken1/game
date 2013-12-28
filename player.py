from point import *
from projectile import *

from config import *
ZERO = point(0, 0)

def sign(x):
	return 1 if x > 0 else -1

def add_col(collisions, time, val):
	if collisions.has_key(time):
		collisions[time].append(val)
	collisions[time] = [val]		

class player:
	def __init__(self, pid, login, game, server):
		self.pid, self.login, self.game, self.server, self.map = pid, login, game, server, game.map

		self.health = MAX_HEALTH
		self.respawn = 1
		
		self.pos = point(0, 0)
		self.speed = point(0, 0)
		self.dv = point(0, 0)

		self.is_start, self.was_action = False, False

		self.weapon = 'K'; self.last_fire_tick = -INF; self.weapon_angle = -1
		self.kills = 0; self.deaths = 0

		self.connects = []

	#---------------------------function for using on client mess---------------------------------#
	def action(self, msg):
		self.was_action = True
		if not self.is_start:
			self.is_start = True

		elif self.game.c_ticks - 1 <= msg['params']['tick'] <= self.game.c_ticks: 
			if msg['action'] != 'empty' and not self.respawn:
				getattr(self, msg['action'])(msg['params'])
		self.game.sync_tick()

	def move(self, params):
		self.dv += point(params['dx'],params['dy'])


	def fire(self, params):
		if self.game.c_ticks - self.last_fire_tick >= weapons[self.weapon].recharge:
			self.last_fire_tick = self.game.c_ticks
			v = point(params['dx'],params['dy'])
			self.weapon_angle = v.angle()
			self.game.projectiles.append(projectile(self, self.weapon,v))
		


	#----------------------------------function for using on tick---------------------------------#
	def resp(self):
		spawn = self.game.get_spawn()
		self.pos = spawn + point(0.5, 0.5)
		self.speed = point(0,0)
		self.health = MAX_HEALTH

	def cur_consist(self):
		self.game.pl_mess.append([
			self.pos.x-1,
			self.pos.y-1,
			self.speed.x,
			self.speed.y,
			self.weapon,
			self.weapon_angle,
			self.login,
			self.health,
			self.respawn,
			self.kills,
			self.deaths
			])

	def above_floor(self):
		if self.map.is_wall(self.pos + point(.5-EPS, .5+EPS)) or\
			self.map.is_wall(self.pos + point(-.5+EPS, .5+EPS)):
			return True
		else: return False

	def speed_calc(self):
		if self.above_floor():
			if self.dv.y < -EPS:
				self.speed.y = -self.game.MAX_SPEED
			if abs(self.dv.x) < EPS:
				if abs(self.speed.x) < self.game.RUB:
					self.speed.x = 0
				else: 
					self.speed.x -= sign(self.speed.x)*self.game.RUB  
		else:
			self.speed.y += self.game.GRAVITY

		if abs(self.dv.x) > EPS:
			self.speed.x += sign(self.dv.x)*self.game.ACCEL
		
		if abs(self.speed.x) > self.game.MAX_SPEED:
			self.speed.x = sign(self.speed.x)*self.game.MAX_SPEED
		if abs(self.speed.y) > self.game.MAX_SPEED:
			self.speed.y = sign(self.speed.y)*self.game.MAX_SPEED
		
		self.dv = ZERO

	def take_item(self, dot):
		dot = dot.to_turple()
		item = self.map.items[dot]
		if not self.game.items[item[0]]:
			self.game.items[item[0]] = RESP_ITEM
			if item[1] == 'h':
				self.health = MAX_HEALTH
			else: 
				self.weapon = item[1]

	def teleport(self, dot):
		self.pos = point(*self.map.tps[dot.to_turple()])
		return

	def peak2peak(self, dist, speed):
		dist_size = dist.size()
		speed_size = speed.size()
		return speed_size > dist_size and\
				(abs(speed.x) < EPS and abs(dist.x) < EPS or\
				abs(speed.y) < EPS and abs(dist.y) < EPS or\
				(speed.scale(dist_size/speed_size) - dist).size()<EPS)

	def go(self):
		speed = self.speed
		if speed.size() < EPS: return
		dir = speed.direct()
		dir1 = point(1 if dir.x else -1, 1 if dir.y else -1)
		#undir = dir.scale(-1,-1)
		center_cell = self.pos.index()
		forward = self.pos + dir1.scale(.5-EPS)
		forward_cell = forward.index()
		forward = self.pos + dir1.scale(.5)
		
		collisions = {}

		dist = forward_cell + dir - forward
		is_reach_x = abs(speed.x) > abs(dist.x); is_reach_y = abs(speed.y) > abs(dist.y);
		if dist.size() < EPS:
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
					elif 'A'<=el<='z': self.take_item(coll_cell)

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
						if abs(self.speed.x) > EPS and abs(self.speed.y) > EPS and coll_cell_wall \
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
						if abs(self.speed.x) > EPS and abs(self.speed.y) > EPS and coll_cell_wall\
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
			self.speed_calc()
			self.go()
		return

	def write_mess(self):
		for c in self.connects:
			if LOGGING:
				log(self.game.mess)
			c.sendMessage(self.game.mess)		
			
	def hit(self, dmg):
		self.health -= dmg
		if self.health <= 0:
		   self.health = 0
		   self.respawn = RESP_PLAYER
		   self.deaths += 1
		   return True
		return False