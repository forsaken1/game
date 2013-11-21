from sympy.geometry import *

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

class map:

	def __init__(self, map, server):
		self.server = server
		self.height, self.width = len(map), len(map[0])	
		self.spawns, self.map = [], []
		self.items, self.tps = {}, {}					# tps - {tps: next_tps}, item - {coord: (number, type)}

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
					if not num_tps.has_key(dot):
					   num_tps[dot] = Point(x,y)
					else:
						self.tps[Point(x,y)] = num_tps[dot].translate(0.5, 0.5)
						self.tps[num_tps[dot]] = Point(x,y).translate(0.5, 0.5)
		self.map.append('#'*self.width)

	def is_wall(self, x):
		return self.map[int(x.y)][int(x.x)] == '#'

	def get_attr(self):
		return [len(self.spawns), len(self.items)]



	def collision_detect(self, start, end, types = all_types_wo_wall()):			# angle bug six
		""" return {dist:{'sq':square, 'pt': coll_point, 'tp':dot_type}}"""

		coll = {}
		seg = Segment(start, end)
		for i in range(min(int(start.y),int(end.y)), max(int(start.y),int(end.y)) + 1):
			for j in range(min(int(start.x),int(end.x)), max(int(start.x),int(end.x)) + 1):
				dot_type = self.map[i][j]
				if dot_type in types:
					pol = Polygon((j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1))
					intersec = pol.intersection(seg)
					if intersec:
						min_dist, min_point = None, None
						for p in intersec:
							if type(p) == Point:
								dist, point = start.distance(p), p
								if min_dist is None or dist < min_dist:
									min_dist, min_point = dist, point
						if not coll.has_key(min_dist):
							coll[min_dist] = [{'sq': Point(j,i),'pt': min_point, 'tp': dot_type}]
						else: 
							coll[min_dist].append({'sq': Point(j,i),'pt': min_point, 'tp': dot_type})
		return coll