class point:

	def __init__(self, x, y):
		self.x, self.y = x, y;

	def __add__(self, other):
		return point(self.x + other.x, self.y + other.y)
	
	def __sub__(self, other):
		return point(self.x - other.x, self.y - other.y)

	def index(self):
		return (int(self.x), int(self.y))

	def to_turple(self):
		return (self.x, self.y)

	def __mul__(self, other):
		return point(self.x*other.x, self.y*other.y)

	def scale(self, k):
		return point(self.x*k, self.y*k)

	def size(self):
		return (self.x*self.x+self.y*self.y)**.5

	def direct(self):
		return point(int(vect.x>=0), int(vect.y>=0))