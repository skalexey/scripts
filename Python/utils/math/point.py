from .vector import Vector


class Point(Vector):
	def __repr__(self):
		return f"Point({self.data})"
	