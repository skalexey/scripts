import asyncio
import threading
import weakref

import utils.collection_utils
import utils.lang
from utils.log.logger import *
from utils.ordered_dict import *

log = Logger()

class Subscription:
	_cb_id = 0
	_lock = threading.Lock()
	# Thread-safe global callback id generator
	@staticmethod
	def _next_cb_id():
		with Subscription._lock:
			cb_id = Subscription._cb_id
			Subscription._cb_id += 1
		return cb_id

	def __init__(self, *args, **kwargs):
		self._data = OrderedDict()
		self._lock = threading.RLock()
		super().__init__(*args, **kwargs)

	class CallableInfo:
		def __init__(self, callable, subscriber, id=None, on_callable_destroyed=None, max_calls=None, unsubscribe_on_false=False, *args, **kwargs):
			# Detect if callable is a bound method
			self.callable_ref = weakref.ref(callable, on_callable_destroyed)
			_subscriber = subscriber if subscriber is not None else utils.lang.extract_self(callable)
			self.subscriber_ref = weakref.ref(_subscriber) if _subscriber is not None else None
			self.id = id
			self.max_calls = max_calls
			self._call_count = 0
			self.unsubscribe_on_false = unsubscribe_on_false
			self._is_valid = True
			super().__init__(*args, **kwargs)
		
		def __repr__(self):
			return f"{self.__class__.__name__}(id={self.id}, callable='{self.callable}', subscriber='{self.subscriber}')"

		@property
		def callable(self):
			return self.callable_ref() if self.callable_ref is not None else None
				
		@property
		def subscriber(self):
			return self.subscriber_ref() if self.subscriber_ref is not None else None

		def _invalidate(self):
			# Keep internal data unchanged for debugging purposes
			self._is_valid = False

		def is_valid(self):
			return self._is_valid

		# Call operator. Returns False if the callable should be unsubscribed
		def __call__(self, *args, **kwargs):
			if not self.is_valid():
				return False
			if self.subscriber_ref is not None and self.subscriber is None:
				self._invalidate()
				# Invalidate before logging to avoid infinite recursion since there are subscriptions on logs
				log.error(f"Subscriber is deleted, but not unsubscribed. Unsubscribing the callable {self}")
				return False
			if self.max_calls is not None:
				if self._call_count >= self.max_calls:
					self._invalidate()
					# Invalidate before logging to avoid infinite recursion since there are subscriptions on logs
					log.error(f"Trying to call a callable '{self}' that has reached ({self._call_count}) its max call count {self.max_calls}, but has not unsubscribed yet for some reason. Unsubscribing it ignoring this call.")
					return False
			result = self.callable(*args, **kwargs)
			self._call_count += 1
			if result is False:
				if self.unsubscribe_on_false:
					log.verbose(f"Callable '{self}' returned False. Unsubscribing it.")
					# Invalidate since other subscribers in the list can do whatever they want
					self._invalidate()
					return False
			if self.max_calls is not None:
				if self._call_count >= self.max_calls:
					log.verbose(f"Callable '{self}' has reached its max call count {self.max_calls}. Unsubscribing it.")
					self._invalidate()
					return False
			return True

		def __eq__(self, other):
			if isinstance(other, Subscription.CallableInfo):
				if self.callable == other.callable:
					subscriber1, subscriber2 = self.subscriber, other.subscriber
					if subscriber1 is None or subscriber2 is None:
						return True
					return subscriber1 == subscriber2
				return False
			return self.callable == other

	class CallableInfoCleanOnDestroy(CallableInfo):
		def __init__(self, callable, subscriber, id, on_callable_destroyed=None, max_calls=None, unsubscribe_on_false=False):
			super().__init__(callable, subscriber, id, on_callable_destroyed, max_calls, unsubscribe_on_false)
			_subscriber = self.subscriber
			if _subscriber is not None:
				# Add __subscriptions__ attribute as a list of callables to the subscriber if not present
				if not hasattr(_subscriber, "__subscriptions__"):
					_subscriber.__subscriptions__ = OrderedDict()
				_subscriber.__subscriptions__.add(id, callable)

		def __del__(self):
			log.verbose(f"__del__({self})")
			subscriber = self.subscriber
			if subscriber is not None:
				subscriber.__subscriptions__.remove(self.id)
				log.verbose(f"CallableInfo {self.id} detached from the subscriber")
				if len(subscriber.__subscriptions__) == 0:
					del subscriber.__subscriptions__
					log.verbose(f"__subscriptions__ attribute removed from the subscriber")

	# Any callable can be passed including another subscription
	def subscribe(self, callable, subscriber=None, max_calls=None, unsubscribe_on_false=False):
		cb_id = self._next_cb_id()
		log.verbose(f"subscribe({callable}, {subscriber}) -> {cb_id}")
		assert cb_id not in self._data.keys()
		def on_callable_destroyed(ref):
			log.verbose(f"on_callable_destroyed({cb_id})")
			assert ref() is None
			if self.unsubscribe(cb_id):
				log.verbose(f"Unsubscribed a deleted subscriber. Callable id: {cb_id}")
		with self._lock:
			self._data[cb_id] = self.CallableInfoCleanOnDestroy(callable, subscriber, cb_id, on_callable_destroyed, max_calls, unsubscribe_on_false)
		return cb_id
	
	def subscribe_once(self, callable, subscriber=None, max_calls=0, unsubscribe_on_false=False):
		cb_to_compare = self.CallableInfo(callable, subscriber)
		cb = utils.collection_utils.find_first(self._data.values(), lambda cb: cb == cb_to_compare)
		if cb is not None:
			return cb.id
		return self.subscribe(callable, subscriber, max_calls, unsubscribe_on_false)

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
			else:
				result = self._unsubscribe_callable(cb_or_id, subscriber)
		log.debug(f"{f'Unsubscribed' if result else 'Already unsubscribed'} callable {cb_or_id}")
		return result

	def notify(self, *args, **kwargs):
		with self._lock:
			to_unsubscribe = []
			for cb in self._data.values().copy():
				if cb(*args, **kwargs) is False:
					to_unsubscribe.append(cb)
			for cb in to_unsubscribe:
				self.unsubscribe(cb)

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
					compare_result = cb.subscriber == any
				if compare_result:
					unsubscribe_ids.append(cb_id)
					result = True
		for cb_id in unsubscribe_ids:
			self.unsubscribe(cb_id)
		return result

	def __call__(self, *args, **kwargs):
		self.notify(*args, **kwargs)
