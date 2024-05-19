import os
import sys
this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, this_dir)
from ordered_dict import *
class Subscription:
	def __init__(self):
		self._data = OrderedDict()
		self._cb_id = 0

	def subscribe(self, callback):
		cb_id = self._cb_id
		self._data[cb_id] = callback
		self._cb_id += 1
		return cb_id
	
	def unsubscribe(self, cb_id):
		del self._data[cb_id]

	def notify(self, *args, **kwargs):
		for cb in self._data.values():
			cb(*args, **kwargs)

	def __iadd__(self, callback):
		self.subscribe(callback)
		return self
