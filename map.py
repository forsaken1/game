from sympy.geometry import *

class map:

	def __init__(self, map, server):
		self.server = server
		self.height, self.width = len(map), len(map[0])	
		self.spawns = self.map = []
		self.items = self.tps = {}					# tps - {tps: next_tps}, item - {coord: (number, type)}

		self.map.append('#'*self.width)
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
					if not num_tps[dot]:
					   num_tps[dot] = Point(x,y)
					else:
						tps[Point(x,y)] = num_tps[dot]
						pts[num_tps[dot]] = Point(x,y)
		self.map.append('#'*self.width)

	def above_floor(self, x):
		return self.map[int(x.y + 1 + self.server.eps)][int(x.x + self.server.eps)] == '#' 

	def get_attr(self):
		return [len(self.spawns), len(self.items)]

	def all_types_wo_wall(self):
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

	def collision_detect(self, start, end, types = self.all_types_wo_wall()):
		""" return {dist:{'sq':square, 'pt': coll_point, 'tp':dot_type}}"""

		coll = {}
		seg = Segment(start, end)
		for i in range(int(start.y), int(end.y) + 1):
			for j in range(int(start.x), int(end.x) + 1):
				dot_type = map[i][j]
				if dot_type in types:
					pol = Polygon((j, i), (j + 1, i), (j + 1, i - 1), (j, i - 1))
					intersec = pol.intersection(seg)
					if intersec:
						min_dist, min_point = start.distance(intersec[0]), intersec[0]
						for p in intersec:
							dist, point = start.distance(p), p
							if dist < min_dist:
								min_dist, min_point = dist, point
						coll[min_dist] = {'sq': Point(j,i),'pt': min_point, 'tp': dot_type}

		return coll