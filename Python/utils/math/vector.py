import math

def iterate_components(any1, any2):
	data1 = any1.data if hasattr(any1, "data") else any1
	data2 = any2.data if hasattr(any2, "data") else any2
	return zip(data1, data2)

class Vector():
	def __init__(self):
		self.data = []

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
	
	def __eq__(self, value: object) -> bool:
		if value is None:
			return False
		return self.data == value.data
	
	def square_distance(self, vec):
		return sum((a - b) ** 2 for a, b in iterate_components(self, vec))
	
	def dot(self, vec):
		return sum(a * b for a, b in iterate_components(self, vec))
		