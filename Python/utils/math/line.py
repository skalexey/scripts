import math
from utils.math.point2 import Point2

class Line():
	def __init__(self, point1, point2):
		self.points = [point1, point2]

	def __repr__(self):
		return f"Line({self.points})"
	
	def __eq__(self, value: object) -> bool:
		# Check if the vectors formed by the lines are equal
		return (self.points[0] - self.points[1]).dot(value.points[0] - value.points[1]) == 0
	
	def sqdistance(self, vec):
		return sum((a - b) ** 2 for a, b in zip(self.data, vec.data))
	
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
	
	def vec(self):
		return self.points[0] - self.points[1]
		