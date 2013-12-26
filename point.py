from math import *

MAX_HEALTH = 100
RESP_ITEM = 300
RESP_PLAYER = 300
INF = 1e6
ROCKET_RADIUS = 1

class weapon():
	def __init__(self, speed, damage, recharge, letter):
		self.speed = speed; self.damage = damage; self.recharge = recharge; self.letter = letter

weapons = {
		   'P': weapon(1, 10, 10,'P'),
		   'M': weapon(1, 10, 5, 'M'),
		   'K': weapon(.5, 5, 3, 'K'),
		   'R': weapon(1, 30, 25, 'R'),
		   'A': weapon(INF, 15, 15, 'A')}


class point:

	def __init__(self, x, y):
		self.x, self.y = x, y;

	def __add__(self, other):
		return point(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other):
		return point(self.x - other.x, self.y - other.y)

	def index(self):
		return point(int(self.x), int(self.y))

	def to_turple(self):
		return (self.x, self.y)

	def __mul__(self, other):
		return point(self.x*other.x, self.y*other.y)

	def scale(self, k):
		return point(self.x*k, self.y*k)

	def size(self):
		return (self.x*self.x+self.y*self.y)**.5

	def direct(self):
		return point(self.x>=0, self.y>=0)

	def angle(self):
		arctg = atan2(self.y, self.x)
		if arctg < 0: arctg+=2*pi
		return arctg/pi*180