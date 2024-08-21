import math
from functools import total_ordering


def iterate_components(any1, any2):
	data1 = getattr(any1, "data", any1)
	data2 = getattr(any2, "data", any2)
	return zip(data1, data2)

@total_ordering
class Vector():
	def __init__(self, data=None, *args, **kwargs):
		self.data = data or []
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"Vector({self.data})"
	
	def __add__(self, value):
		this_class = self.__class__
		# Instantiate a new object of the same class
		return this_class([a + b for a, b in iterate_components(self, value)])

	def __sub__(self, value):
		this_class = self.__class__
		# Instantiate a new object of the same class
		return this_class([a - b for a, b in iterate_components(self, value)])

	def __mul__(self, value):
		this_class = self.__class__
		# Instantiate a new object of the same class
		return this_class([a * value for a in self.data])
	
	def __truediv__(self, value):
		this_class = self.__class__
		# Instantiate a new object of the same class
		return this_class([a / value for a in self.data])
	
	def __eq__(self, value) -> bool:
		if value is None:
			return False
		if not isinstance(value, Vector):
			return False
		return self.data == value.data
	
	def __lt__(self, value) -> bool:
		return self.sqmagnitude() < value.sqmagnitude()
	
	def sqdistance(self, vec):
		return sum((a - b) ** 2 for a, b in iterate_components(self, vec))
	
	def dot(self, vec):
		return sum(a * b for a, b in iterate_components(self, vec))
	
	def cross(self, vec):
		return self.data[0] * vec.data[1] - self.data[1] * vec.data[0]
		
	def normalize(self):
		magnitude = self.magnitude()
		return self / magnitude
	
	def sqmagnitude(self):
		return sum(a ** 2 for a in self.data)
	
	def magnitude(self):
		return math.sqrt(self.sqmagnitude())
	