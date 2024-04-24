from utils.math.vector import *

class Vector2(Vector):
	def __init__(self, x = 0, y = 0):
		super().__init__()
		self.data = [x, y]
	
	def __repr__(self):
		return f"Vector2({self.data})"
	
	def is_up(self):
		return self.dot(Vector2(1, 0)) == 0
	
	def is_down(self):
		return self.dot(Vector2(-1, 0)) == 0