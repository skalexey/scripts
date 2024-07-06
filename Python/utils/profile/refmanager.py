import weakref

from utils.intrstate import Intrstate


class RefManager(Intrstate):
	def _process_set_value(self, key, value):
		return weakref.ref(value)

	def _process_get_value(self, key, value):
		return value()
