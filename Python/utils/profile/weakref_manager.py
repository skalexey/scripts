import weakref

from utils.intrstate import Intrstate


class WeakrefManager(Intrstate):
	"""
	An object that wraps each attribute assigned to it in a weak reference and returns the dereferenced object when the attribute is accessed.
	"""

	def _process_set_value(self, key, value):
		return weakref.ref(value)

	def _process_get_value(self, key, value):
		return value()
