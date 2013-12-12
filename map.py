from sympy.geometry import *



class map:

	def __init__(self, map, server):
		self.server = server
		self.height, self.width = len(map), len(map[0])	
		self.spawns, self.map = [], []
		self.items, self.tps = {}, {}					# tps - {tps: next_tps}, item - {coord: (number, type)}

		self.map.append('#'*(self.width+2))
		num_tps = {}
		num_item = 0
		for i in range(self.height):				# coordinates w/o border
			self.map.append("#" + map[i] + "#")
			for j in range(self.width):
				dot = map[i][j]
				x, y = j+1, i+1
				if dot == '$': 
					self.spawns.append(Point(x,y))
				if 'a' <= dot <= 'Z': 
					self.items[Point(x,y)] = (num_item, dot)
					num_item +=1
				if '0' <= dot <= '9': 
					if not num_tps.has_key(dot):
					   num_tps[dot] = Point(x,y)
					else:
						self.tps[Point(x,y)] = num_tps[dot].translate(0.5, 0.5)
						self.tps[num_tps[dot]] = Point(x,y).translate(0.5, 0.5)
		self.map.append('#'*(self.width+2))

	def is_wall(self, x):
		return self.map[int(x.y)][int(x.x)] == '#'

	def el_by_point(self, point):
		return self.map[int(point.y)][int(point.x)]

	def get_attr(self):
		return [len(self.spawns), len(self.items)]


