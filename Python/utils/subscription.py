import os
import sys

this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, this_dir)
from ordered_dict import *


class Subscription:
	def __init__(self):
		self._data = OrderedDict()
		self._cb_id = 0

	# Any callable can be passed including another subscription
	def subscribe(self, callable):
		cb_id = self._cb_id
		self._data[cb_id] = callable
		self._cb_id += 1
		return cb_id
	
	def unsubscribe(self, cb_id):
		del self._data[cb_id]

	def notify(self, *args, **kwargs):
		for cb in self._data.values().copy():
			cb(*args, **kwargs)

	def wait(self, timeout=None):
		event = threading.Event()
		def on_notify(*args, **kwargs):
			event.set()
		cb_id = self.subscribe(on_notify)
		event.wait(timeout)
		self.unsubscribe(cb_id)
		return event.is_set()
			
	async def asyncio_wait(self, timeout=None):
		event = asyncio.Event()
		def on_notify(*args, **kwargs):
			event.set()
		cb_id = self.subscribe(on_notify)
		await asyncio.wait_for(event.wait(), timeout)
		self.unsubscribe(cb_id)
		return event.is_set()

	def __iadd__(self, callable):
		self.subscribe(callable)
		return self
	
	def __isub__(self, callable):
		unsubscribe_ids = []
		for cb_id, cb in self._data.items():
			if cb == callable:
				unsubscribe_ids.append(cb_id)
		for cb_id in unsubscribe_ids:
			self.unsubscribe(cb_id)

	def __call__(self, *args, **kwargs):
		self.notify(*args, **kwargs)
