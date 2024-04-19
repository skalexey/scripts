
from utils.math.point import Point

class Point2(Point):
	def __init__(self, *args):
		super().__init__()

		if len(args) == 2:
			# If two arguments are provided, assume they are x and y coordinates
			self.data = list(args)
		elif len(args) == 1:
			# If only one argument is provided, assume it is a list or tuple containing x and y coordinates
			assert len(args[0]) == 2, "Data must contain exactly two elements"
			self.data = list(args[0])
		else:
			raise ValueError("Invalid number of arguments")
	
	def x(self):
		return self.data[0]
	
	def y(self):
		return self.data[1]

	def __repr__(self):
		return f"Point2({self.data})"
	