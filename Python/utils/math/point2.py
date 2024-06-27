import utils.serialize

from .point import *


class Point2(Point, utils.serialize.Serializable):
	def __init__(self, *args, x=None, y=None, data=None, **kwargs):
		_data = data
		if (x is not None and y is None) or (x is None and y is not None):
			raise ValueError(utils.function.msg("Both x and y must be provided, or data"))
		if data is not None and (x is not None or y is not None):
			raise ValueError(utils.function.msg("Cannot provide both data and x, y"))
		if len(args) == 2:
			# If two arguments are provided, assume they are x and y coordinates
			if x is not None or y is not None:
				raise ValueError(utils.function.msg("Multiple values for x, y provided"))
			if data is not None:
				raise ValueError(utils.function.msg("data was provided though kwargs having x, y provided positionally"))
			_data = list(args)
		elif len(args) == 1:
			if x is not None or y is not None:
				raise ValueError(utils.function.msg("Cannot provide both data and x, y"))
			# If only one argument is provided, assume it is a list or tuple containing x and y coordinates
			if len(args[0]) != 2:
				raise ValueError(utils.function.msg("Data must contain exactly two elements"))
			if data is not None:
				raise ValueError(utils.function.msg("Multiple values for data provided"))
			_data = list(args[0])
		elif len(args) == 0:
			# If no arguments provided, assume the point is at the origin
			_data = [x or 0, y or 0]
		else:
			raise ValueError(utils.function.msg("Invalid number of arguments"))
		if _data is None:
			raise ValueError(utils.function.msg("Unexpected error"))
		super().__init__(_data
			, assign_attrs=False # Assign attributes manually since no information provided to the assignment algorithm on how to distribute *args
			, **kwargs) # Carrying over arguments is not supported yet
	
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

	def __str__(self):
		return f"({self.x}, {self.y})"

	def serialize(self, **kwargs):
		return super().serialize(ignore="data", **kwargs)
