import asyncio
import threading
from time import sleep, time

import utils  # Lazy import for less important modules
import utils.collection
import utils.lang
import utils.method
from utils.collection.ordered_dict import OrderedDict
from utils.collection.ordered_set import OrderedSet
from utils.concurrency.scoped_lock import ScopedLock
from utils.context import GlobalContext
from utils.debug import wrap_debug_lock
from utils.live import verify
from utils.log.logger import Logger
from utils.memory import OwnedCallable, SmartCallable
from utils.timed_loop import timed_loop

log = Logger()

class Subscription:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data = OrderedDict()
		self._priorities = {}
		self._lock = wrap_debug_lock(threading.RLock())#, timeout=0.3)
		# self._lock = threading.RLock()

	class CallableInfo(OwnedCallable):
		def __init__(self, *args, unsubscribe_on_false=None, priority=None, **kwargs):
			super().__init__(*args, invalidate_on_false=unsubscribe_on_false, **kwargs)
			self.priority = priority or 0
		
	class CallableInfoCleanOnDestroy(CallableInfo, SmartCallable):
		pass

	# Any callable can be passed including another subscription
	def _subscribe(self, callable, subscriber=None, caller=None, max_calls=None, unsubscribe_on_false=None, priority=None):
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
		return cb
	
	def subscribe(self, *args, **kwargs):
		return self._subscribe(*args, **kwargs).id
	
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
		for state in timed_loop(3):
			with self._lock:
				cb_locks = []
				priorities = self._priorities.values()
				for priority_group in priorities:
					for i, cb_id in enumerate(priority_group):
						cb = self._data[cb_id]
						cb_locks.append(cb._invalidate_lock)
						# log.debug(utils.method.msg(f"Added lock {i + 1}: '{cb._invalidate_lock}' of cb {cb} (id: {cb_id})"))
				with ScopedLock(*cb_locks, timeout=0) as ndl: # TODO: Consider non blocking, or a bit more bigger timeout
					if not ndl.locked():
						sleep(0.01)
						continue
					for priority_group in list(reversed(priorities)): # Copy is needed due to the fact that callables can be unsubscribed through the notification call
						for cb_id in priority_group.copy():
							cb = self._data[cb_id]
							cb(*args, **kwargs)
							# if cb.is_invalidated(): # Should be unsubscribed through on_invalidated callback
							if cb._invalidated: # Use is_invalidated() if haven't locked _invalidate_lock manually as above.
								if self.is_subscribed(cb.id): # Should be unsubscribed through on_invalidated callback if invalidated
									raise RuntimeError(f"Callable {cb} has been invalidated, but not unsubscribed")
					break
		if state.timedout:
			raise RuntimeError(utils.method.msg(f"Failed to acquire all locks in time of 3 seconds (self={self})"))

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
					compare_result = cb.owner == any or cb.cb_self == any
				if compare_result:
					unsubscribe_ids.append(cb_id)
					result = True
		for cb_id in unsubscribe_ids:
			self.unsubscribe(cb_id)
		return result

	def subscriber_count(self):
		return len(self._data)

	def __call__(self, *args, **kwargs):
		self.notify(*args, **kwargs)

# Notification happens only once and any subscriptions following the notification trigger the notification on the subscriber.
class OneTimeSubscriptionBase(Subscription):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._result = None

	def _set_result(self, *args, **kwargs):
		self.notify(*args, **kwargs)

	def _reset_result(self):
		self._result = None

	def notify(self, *args, **kwargs):
		verify(self._result is None, utils.method.msg("Result is already set"))
		self._result = args, kwargs
		super().notify(*args, **kwargs)

	def subscribe(self, callable, subscriber=None, *args, **kwargs):
		cb = super()._subscribe(callable, subscriber, *args, **kwargs)
		if self._result is not None:
			cb(self._result)

class OneTimeSubscription(OneTimeSubscriptionBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def result(self, timeout=None):
		if self._result is None:
			if not self.wait(timeout):
				raise TimeoutError(utils.method.msg_kw("Timeout occured while waiting for event"))
		return self._result
	
	def set_result(self, *args, **kwargs):
		self._set_result(*args, **kwargs)

	def reset_result(self):
		self._reset_result()


class Event(OneTimeSubscriptionBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def set(self):
		self._set_result()

	def is_set(self):
		return self._result is not None

	def reset(self):
		self._result = None

	def notify(self): # Override for making no args allowed
		super().notify()
