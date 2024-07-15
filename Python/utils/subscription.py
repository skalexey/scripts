import asyncio
import threading
import weakref

import utils.collection
import utils.lang
from utils.collection.ordered_dict import OrderedDict
from utils.collection.ordered_set import OrderedSet
from utils.log.logger import Logger
from utils.memory import OwnedCallable, SmartCallable

log = Logger()

class Subscription:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data = OrderedDict()
		self._priorities = {}
		self._lock = threading.RLock()

	class CallableInfo(OwnedCallable):
		def __init__(self, *args, unsubscribe_on_false=None, priority=None, **kwargs):
			super().__init__(*args, invalidate_on_false=unsubscribe_on_false, **kwargs)
			self.priority = priority or 0
		
	class CallableInfoCleanOnDestroy(CallableInfo, SmartCallable):
		pass

	# Any callable can be passed including another subscription
	def subscribe(self, callable, subscriber=None, caller=None, max_calls=None, unsubscribe_on_false=None, priority=None):
		def on_invalidated(cb, self_weak=utils.memory.weak_proxy(self)):
			assert not cb.is_valid(), f"Callable {cb} should have been invalidated, but is still valid"
			if not self_weak.is_alive():
				log.verbose(utils.function.msg(f"{cb}: self_weak is dead"))
				return
			if self_weak.unsubscribe(cb.id):
				log.verbose(utils.function.msg(f"Unsubscribed invalidated callable: {cb}"))
			else:
				log.verbose(utils.function.msg(f"Callable is already unsubscribed: {cb}"))
		with self._lock:
			cb = self.CallableInfoCleanOnDestroy(callable, subscriber, caller, on_invalidated=on_invalidated, max_calls=max_calls, unsubscribe_on_false=unsubscribe_on_false, priority=priority)
			log.verbose(f"subscribe({callable}, {subscriber}) -> {cb.id}")
			assert cb.id not in self._data.keys()
			self._data[cb.id] = cb
			self._assign_priority(cb.id, cb.priority)
		return cb.id
	
	def _assign_priority(self, cb_id, priority):
		priority_group = self._priorities.get(priority)
		if priority_group is None:
			priority_group = OrderedSet()
			self._priorities[priority] = priority_group
		priority_group.add(cb_id)

	def _remove_priority(self, cb_id, priority):
		priority_group = self._priorities[priority]
		priority_group.remove(cb_id)
		if len(priority_group) == 0:
			self._priorities.pop(priority)

	def subscribe_once(self, callable, subscriber=None, *args, **kwargs):
		cb_to_compare = self.CallableInfo(callable, subscriber)
		cb = utils.collection.find_first(self._data.values(), lambda cb: cb == cb_to_compare)
		if cb is not None:
			return cb.id
		return self.subscribe(callable, subscriber, *args, **kwargs)

	def is_subscribed(self, cb_or_id):
		with self._lock:
			if isinstance(cb_or_id, int):
				return cb_or_id in self._data.keys()
			return any(cb == cb_or_id for cb in self._data.values())
	
	def unsubscribe(self, cb_or_id, subscriber=None):
		result = False
		with self._lock:
			if isinstance(cb_or_id, int):
				cb = self._data.pop(cb_or_id, None)
				if cb is not None:
					result = True
					self._remove_priority(cb_or_id, cb.priority)
			else:
				result = self._unsubscribe_callable(cb_or_id, subscriber)
		log.verbose(f"{f'Unsubscribed' if result else 'Already unsubscribed'} callable {cb_or_id}")
		return result

	def notify(self, *args, **kwargs):
		if not self._priorities:
			return
		with self._lock:
			for priority_group in list(self._priorities.values()):
				for cb_id in priority_group.copy():
					cb = self._data[cb_id]
					cb(*args, **kwargs)
					if not cb.is_valid(): # Should be unsubscribed through on_invalidated callback
						if self.is_subscribed(cb.id):
							raise RuntimeError(f"Callable {cb} has been invalidated, but not unsubscribed")

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

	def _unsubscribe_callable(self, any, subscriber=None):
		unsubscribe_ids = []
		result = False
		with self._lock:
			for cb_id, cb in self._data.items():
				if isinstance(any, int):
					compare_result = cb_id == any
				elif isinstance(any, self.CallableInfo):
					compare_result = cb == any
				elif callable(any):
					cb_to_compare = self.CallableInfo(any, subscriber)
					compare_result = cb == cb_to_compare
				else:
					compare_result = cb.owner == any
				if compare_result:
					unsubscribe_ids.append(cb_id)
					result = True
		for cb_id in unsubscribe_ids:
			self.unsubscribe(cb_id)
		return result

	def __call__(self, *args, **kwargs):
		self.notify(*args, **kwargs)
