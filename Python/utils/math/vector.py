import math

class Vector():
	def __init__(self):
		self.data = []

	def __repr__(self):
		return f"Vector({self.data})"
	
	def __eq__(self, value: object) -> bool:
		return self.data == value.data
	
	def square_distance(self, vec):
		return sum((a - b) ** 2 for a, b in zip(self.data, vec.data))
	
	def dot(self, vec):
		return sum(a * b for a, b in zip(self.data, vec.data))
		