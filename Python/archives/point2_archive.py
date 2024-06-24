from .point import *


class Point2(Point):
	def __init__(self, *args, x=None, y=None, data=None):
		super().__init__()
		x = kwargs.get("x", None)
		y = kwargs.get("y", None)
		data = kwargs.get("data", None)
		if data is not None and (x is not None or y is not None):
			raise ValueError(utils.function.msg("Cannot provide both data and x/y"))
		if y is None:
			if x is not None:
				# Consider the first argument 
		if len(args) == 2:
			# If two arguments are provided, assume they are x and y coordinates
			if x is not None or y is not None:
				raise ValueError(utils.function.msg("Multiple values for x/y provided"))
			x, y = args
		elif len(args) == 1:
			# If only one argument is provided, assume it is a list or tuple containing x and y coordinates
			if len(args[0]) != 2:
				raise ValueError(utils.function.msg("Data must contain exactly two elements"))
			if data is not None:
				raise ValueError(utils.function.msg("Multiple values for data provided"))
			self.data = list(args[0])
		elif len(args) == 0:
			# If no arguments provided, assume the point is at the origin
			self.data = [0, 0]
		else:
			raise ValueError(utils.function.msg("Invalid number of arguments"))
	
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
	
