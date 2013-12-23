from point import *

weapons = {			# (speed, damage, recharge)
		   'P': (1, 10, 10,'P'),
		   'M': (1, 10, 5, 'M'),
		   'K': (.5, 5, 3, 'K'),
		   'R': (1, 30, 25, 'R'),
		   'A': (100000, 15, 15, 'A')}

class projectile():
	def __init__(self, player, weapon, v):					# todo zero division
		self.game = player.game; self.map = player.map; self.player = player
		self.weapon = weapons[weapon]; self.v = v.scale(self.weapon[0]/ v.size())
		self.pos = player.pos; self.index = self.pos.index()
		self.k = v.y/v.x; self.b = self.pos.y - self.k*self.pos.x
		self.dir = v.direct()
		self.dir1 = point(1 if self.dir.x else -1, 1 if self.dir.y else -1)
		self.was_coll = False; self.life_time = 0;

	def go(self):
		index = self.index
		pos = self.pos
		dir = self.dir; dir1 = self.dir1
		end = pos + self.v
		end = point(int(end.x), int(end.y))
		while True:
			last = int((index.x+dir.x)*self.k + self.b)
			while index.y != last:
				index.y += dir1.y
				if self.map.map[index.y][index.x] == '#':
					self.was_coll = True
					self.v = self.v.scale(abs((index.y+(not dir.y)) - self.pos.y)/self.v.y)
					return
				if index.y == end.y and index.x == end.x:
					return; 
			index.x += dir1.x
			if self.map.map[index.y][index.x] == '#':
				self.was_coll = True
				self.v = self.v.scale(abs(index.x + dir.x - pos.x)/self.v.x)
				return
			if index.y == end.y and index.x == end.x:
				return; 
			
	def player_coll(self):
		dir1 = self.dir1
		v = self.v
		min_dist = abs(v.y)
		end = self.pos + v
		pos = self.pos
		k = self.k; b = self.b
		damaged = 0
		for pl in self.game.players:
			x = pl.pos.x - dir1.x*.5
			if not pl.respawn and (x < pos.x) ^ (x < end.x) and abs(k*x+b-pl.pos.y) <= .5 and abs(x-pos.x)*k<min_dist:
				min_dist = abs(x-pos.x)*k
				damaged = pl
			else:
				y = pl.pos.y - dir1.y*.5
				if (y < pos.y) ^ (y < end.y) and abs((y-b)/k-pl.pos.x) <= .5 and abs(y-pos.y)<min_dist:
					min_dist = abs(y-pos.y)
					damaged = pl
		if damaged:
			self.v = v.scale(min_dist/abs(v.y))
			self.was_coll = True
			if damaged.hit(weapon[1]):
				self.player.kills += 1

	def cur_consist(self):
		self.game.pr_mess.append([
			self.pos.x-1,
			self.pos.y-1,
			self.v.x,
			self.v.y,
			self.weapon[3],
			self.life_time
			])


	def tick(self):
		if self.weapon[3] == 'K' and self.life_time > 0:
			self.game.projectiles.remove(self)
			return
		self.life_time += 1
		if self.v.size() == 0:
			self.cur_consist()
			self.game.projectiles.remove(self)
		else:
			self.go()
			self.player_coll()
			self.cur_consist()
			self.pos += self.v
		
		if self.was_coll:
			self.v = point(0,0)