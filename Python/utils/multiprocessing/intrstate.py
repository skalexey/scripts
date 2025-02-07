import multiprocessing

from utils.intrstate import Intrstate


class MultiprocessIntrstate(Intrstate):
	"""
	Ensures the intrinsic state of an object remains unchanged by storing all user attributes in a separate _state dictionary.
	This approach is useful for representing a data block as an object while concealing control information from the user.
	"""

	def __init__(self, *args, state=None,  **kwargs):
		_state = state or multiprocessing.Manager().dict()
		super().__init__(*args, **kwargs, state=_state)
