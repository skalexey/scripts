from .point2 import *
from .vector2 import *


class Line():
	def __init__(self, point1, point2):
		assert point1 != point2	
		self.points = [point1, point2]
		super().__init__()

	def __repr__(self):
		return f"{self.__class__.__name__}({self.points})"
	
	def __eq__(self, value: object) -> bool:
		if not isinstance(value, Line):
			return False
		# Check if the vectors formed by the lines are equal
		vec1 = self.vec()
		vec2 = value.vec()
		cross_product = vec1.cross(vec2)
		if cross_product != 0:
			return False
		# Check if the lines share at least one point
		vec3 = value.points[0] - self.points[0]
		cross_product_2 = vec1.cross(vec3)
		if cross_product_2 != 0:
			return False
		return True
	
	def sqdistance(self, point):
		# https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
		x1, y1 = self.points[0].data
		x2, y2 = self.points[1].data
		x3, y3 = point.data
		return abs((y2 - y1) * x3 - (x2 - x1) * y3 + x2 * y1 - y2 * x1) ** 2 / ((y2 - y1) ** 2 + (x2 - x1) ** 2)
	
	def intersection(self, line):
		# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
		x1, y1 = self.points[0].data
		x2, y2 = self.points[1].data
		x3, y3 = line.points[0].data
		x4, y4 = line.points[1].data
		denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
		if denominator == 0:
			return None
		t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
		u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
		if 0 <= t <= 1 and 0 <= u <= 1:
			return Point2(x1 + t * (x2 - x1), y1 + t * (y2 - y1))
		return None
	
	# Find an intersection point between infinitely long lines defined by the points given two points on each line
	def rays_intersection(self, line):
		# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
		x1, y1 = self.points[0].data
		x2, y2 = self.points[1].data
		x3, y3 = line.points[0].data
		x4, y4 = line.points[1].data
		denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
		# When the two lines are parallel or coincident, the denominator is zero
		return Point2(
			((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denominator,
			((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denominator
		)
	
	def vec(self, point_traverse_direction=Vector2(1, 0)): # Default direction is right
		if self.points[0] == self.points[1]:
			raise ValueError("The contains 2 same points.")
		result = (self.points[1] - self.points[0]) * point_traverse_direction.x
		assert result.x >= 0
		return result