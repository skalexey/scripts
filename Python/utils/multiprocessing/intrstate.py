import multiprocessing

from utils.intrstate import Intrstate


class MultiprocessIntrstate(Intrstate):
	"""
	Ensures the intrinsic state of an object remains unchanged by storing all user attributes in a separate _state dictionary.
	This approach is useful for representing a data block as an object while concealing control information from the user.
	"""

	def __init__(self, state=None, *args, **kwargs):
		if state is not None:
			self._state = state
		else:
			if self._state is None:
				self._state = multiprocessing.Manager().dict()
		super().__init__(*args, **kwargs)
