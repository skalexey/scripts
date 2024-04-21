
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
	
	def _get_x(self):
		return self.data[0]

	def _set_x(self, value):
		self.data[0] = value

	def _get_y(self):
		return self.data[1]

	def _set_y(self, value):
		self.data[1] = value

	x = property(
		fget=_get_x,
		fset=_set_x,
		doc="The x coordinate property."
	)

	y = property(
		fget=_get_y,
		fset=_set_y,
		doc="The y coordinate property."
	)

	def __repr__(self):
		return f"Point2({self.data})"
	