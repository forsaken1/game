from sympy.geometry import *

class map:

	def __init__(self, map):
		self.height = len(map)
		self.width = len(map[0])			
		self.spawns = []
		self.items = {}
		self.tps = {}
		self.map = []

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

	def get_attr(self):
		return [len(self.spawns), len(self.items)]

	def collis_detect(self, start, end):
		""" ret type == {dist:(rect, coll_point)} sorted by dist"""

		coll = {}
		seg = Segment(start, end)
		for i in range(int(start.y), int(end.y) + 1):
			for j in range(int(start.x), int(end.x) + 1):
				if map[i][j] == type:
					pol = Polygon((j, i), (j + 1, i), (j + 1, i - 1), (j, i - 1))
					intersec = pol.intersection(seg)
					if intersec:
						min_dist, min_point = start.distance(intersec[0]), intersec[0]
						for p in intersec:
							dist, point = start.distance(p), p
							if dist < min_dist:
								min_dist, min_point = dist, point
						coll[min_dist] = (Point(j,i), min_point)

		return coll