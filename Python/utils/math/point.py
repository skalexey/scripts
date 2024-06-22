from .vector import Vector


class Point(Vector):
	def __init__(self):
		self.data = []
		super().__init__()

	def __repr__(self):
		return f"Point({self.data})"
	