from .vector import Vector


class Point(Vector):
	def __init__(self):
		self.data = []

	def __repr__(self):
		return f"Point({self.data})"
	