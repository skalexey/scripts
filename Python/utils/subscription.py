import threading
import weakref

import utils.lang
from utils.log.logger import *
from utils.ordered_dict import *

logger = Logger()

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

	def __init__(self):
		self._data = OrderedDict()

	class CallableInfo:
		def __init__(self, callable_ref, subscriber_ref, id):
			self.callable_ref = callable_ref
			self.subscriber_ref = subscriber_ref
			self.id = id
		
		def __repr__(self):
			return f"CallableInfo(id={self.id})"

		def __del__(self):
			logger.log_debug(f"__del__({self})")
			subscriber = self.subscriber
			if subscriber is not None:
				subscriber.__subscriptions__.remove(self.id)
				logger.log_debug(f"CallableInfo {self.id} detached from the subscriber")
				if len(subscriber.__subscriptions__) == 0:
					del subscriber.__subscriptions__
					logger.log_debug(f"__subscriptions__ attribute removed from the subscriber")
			
		@property
		def callable(self):
			return self.callable_ref() if self.callable_ref is not None else None
				
		@property
		def subscriber(self):
			return self.subscriber_ref() if self.subscriber_ref is not None else None

		# Call operator
		def __call__(self, *args, **kwargs):
			if self.subscriber_ref is not None:
				assert(self.subscriber_ref is None or self.subscriber is not None)
				return self.callable(*args, **kwargs)
			return self.callable(*args, **kwargs)

		def __eq__(self, other):
			if isinstance(other, Callable):
				if self.callable == other.callable:
					if self.subscriber_ref is not None:
						return self.subscriber_ref() == other.subscriber_ref()
					return True
				return False
			return self.callable == other

	# Any callable can be passed including another subscription
	def subscribe(self, callable, subscriber=None):
		cb_id = self._next_cb_id()
		logger.log_debug(f"subscribe({callable}, {subscriber}) -> {cb_id}")
		assert(cb_id not in self._data.keys())
		# Detect if callable is a bound method
		_subscriber = subscriber
		if _subscriber is None and hasattr(callable, '__self__') and callable.__self__ is not None:
			_subscriber = callable.__self__
			logger.log_debug(f"Bound method detected. It contains the subscriber: {subscriber}")
		def on_callable_destroyed(ref):
			logger.log_debug(f"on_callable_destroyed({cb_id})")
			assert ref() is None
			if self.unsubscribe(cb_id):
				logger.log_debug(f"Unsubscribed a deleted subscriber. Callable id: {cb_id}")
		callable_ref = weakref.ref(callable, on_callable_destroyed)
		if _subscriber is not None:
			# Add __subscriptions__ attribute as a list of callables to the subscriber if not present
			if not hasattr(_subscriber, "__subscriptions__"):
				_subscriber.__subscriptions__ = OrderedDict()
			_subscriber.__subscriptions__.add(cb_id, callable)
			subscriber_ref = weakref.ref(_subscriber)
		else:
			subscriber_ref = None
		self._data[cb_id] = self.CallableInfo(callable_ref, subscriber_ref, cb_id)
		return cb_id
	
	def is_subscribed(self, cb_or_id):
		if isinstance(cb_or_id, int):
			return cb_or_id in self._data.keys()
		return any(cb == cb_or_id for cb in self._data.values())
	
	def unsubscribe(self, cb_or_id, subscriber=None):
		result = False
		if isinstance(cb_or_id, int):
			cb = self._data.pop(cb_or_id)
			if cb is not None:
				result = True
		else:
			result = self._unsubscribe_callable(cb_or_id, subscriber)
		logger.log_debug(f"{f'Unsubscribed' if result else 'Already unsubscribed'} callable {cb_or_id}")
		return result

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

	def _unsubscribe_callable(self, callable, subscriber=None):
		unsubscribe_ids = []
		result = False
		for cb_id, cb in self._data.items():
			if cb.callable == callable and cb.subscriber == subscriber:
				unsubscribe_ids.append(cb_id)
				result = True
		for cb_id in unsubscribe_ids:
			self.unsubscribe(cb_id)
		return result

	def __call__(self, *args, **kwargs):
		self.notify(*args, **kwargs)
