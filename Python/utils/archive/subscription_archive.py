class CallableInfo:
		def __init__(self, callable, subscriber, id=None, caller=None, on_invalidated=None, max_calls=None, unsubscribe_on_false=None, priority=None, *args, **kwargs):
			# Detect if callable is a bound method
			cb = utils.inspect_utils.function(callable) or callable
			self.callable_ref = weakref.ref(cb, on_invalidated)
			cb_self = caller or utils.lang.extract_self(callable)
			self.cb_self_ref = weakref.ref(cb_self, on_invalidated) if cb_self is not None else None
			_subscriber = subscriber#subscriber if subscriber is not None else cb_self
			self.subscriber_ref = weakref.ref(_subscriber, on_invalidated) if _subscriber is not None else None
			self.id = id
			self.max_calls = max_calls
			self._call_count = 0
			self.unsubscribe_on_false = unsubscribe_on_false or False
			self.priority = priority or 0
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

		@property
		def cb_self(self):
			return self.cb_self_ref() if self.cb_self_ref is not None else None

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
			if self.callable_ref is not None and self.callable is None:
				self._invalidate()
				# Invalidate before logging to avoid infinite recursion since there are subscriptions on logs
				log.error(f"Callable is deleted, but not unsubscribed. Unsubscribing the callable {self}")
				return False
			if self.max_calls is not None:
				if self._call_count >= self.max_calls:
					self._invalidate()
					# Invalidate before logging to avoid infinite recursion since there are subscriptions on logs
					log.error(f"Trying to call a callable '{self}' that has reached ({self._call_count}) its max call count {self.max_calls}, but has not unsubscribed yet for some reason. Unsubscribing it ignoring this call.")
					return False
			cb_self = self.cb_self
			_args = [cb_self] + list(args) if cb_self is not None else args
			result = self.callable(*_args, **kwargs)
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
			if not self.callable == other:
				return utils.inspect_utils.function(other) == self.callable
			return True

	class CallableInfoCleanOnDestroy(CallableInfo):
		def __init__(self, callable, subscriber, id, *args, **kwargs):
			super().__init__(callable, subscriber, id, *args, **kwargs)
			if subscriber is not None:
				# Add __subscriptions__ attribute as a list of callables to the subscriber if not present
				if not hasattr(subscriber, "__subscriptions__"):
					subscriber.__subscriptions__ = OrderedDict()
				cb = utils.inspect_utils.function(callable) or callable
				subscriber.__subscriptions__.add(id, cb)

		def __del__(self):
			log.verbose(f"__del__({self})")
			subscriber = self.subscriber
			if subscriber is not None:
				subscriptions = getattr(subscriber, "__subscriptions__", None)
				if subscriptions is not None:
					subscriber.__subscriptions__.remove(self.id)
					log.verbose(f"CallableInfo {self.id} detached from the subscriber")
					if len(subscriber.__subscriptions__) == 0:
						del subscriber.__subscriptions__
						log.verbose(f"__subscriptions__ attribute removed from the subscriber")