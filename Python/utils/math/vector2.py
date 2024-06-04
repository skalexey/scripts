from .vector import *


class Vector2(Vector):
	# Variadic parameters
	def __init__(self, *args):
		data = None
		if len(args) == 1:
			data = args[0]
		elif len(args) == 2:
			data = [args[0], args[1]]
		else:
			raise ValueError("Invalid number of arguments.")
		super().__init__(data)
	
	def __repr__(self):
		return f"Vector2({self.data})"
	
	def is_up(self):
		return self.dot(Vector2(1, 0)) == 0
	
	def is_down(self):
		return self.dot(Vector2(-1, 0)) == 0
	
	@property
	def x(self):
		return self.data[0]
	
	@x.setter
	def x(self, value):
		self.data[0] = value

	@property
	def y(self):
		return self.data[1]
	
	@y.setter
	def y(self, value):
		self.data[1] = value