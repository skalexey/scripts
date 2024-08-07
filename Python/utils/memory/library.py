import threading
import weakref
from functools import partial, wraps

import utils.function
import utils.inspect_utils as inspect_utils
import utils.lang
import utils.method
from utils.collection.ordered_dict import OrderedDict
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger
from utils.profile.trackable_resource import TrackableResource

log = Logger()


class Callable(TrackableResource):
	def __init__(self, callable, caller=None, on_invalidated=None, max_calls=None, invalidate_on_false=None, args=None, kwargs=None, *other_args, **other_kwargs):
		# Initialized first for repr
		self._args = args
		self._kwargs = kwargs
		self._invalidated = False
		self._on_invalidated = on_invalidated
		self._invalidate_lock = wrap_debug_lock(threading.RLock()) # Test it more with Lock with turned off logs in ParameterizedLock and ScopedLock
		self.max_calls = max_calls
		self._call_count = 0
		self.invalidate_on_false = invalidate_on_false or False
		# Detect if callable is a bound method
		cb = inspect_utils.function(callable) or callable
		_on_refobj_destroyed = self.gen_refobj_destroyed_cb()
		self.callable_ref = weakref.ref(cb, _on_refobj_destroyed)
		log.verbose(utils.function.msg(f"Callable weak reference {self.callable_ref} created"))
		cb_self = caller or utils.lang.extract_self(callable)
		self.cb_self_ref = weakref.ref(cb_self, _on_refobj_destroyed) if cb_self is not None else None
		if self.cb_self_ref is not None:
			log.verbose(utils.function.msg(f"Caller weak reference {self.cb_self_ref} created"))
		super().__init__(*other_args, **other_kwargs)
	
	def __del__(self):
		log.verbose(utils.function.msg_kw())
		if not self.is_invalidated():
			self._invalidate()
		utils.lang.safe_super(Callable, self).__del__()

	def gen_refobj_destroyed_cb(self, on_refobj_destroyed=None):
		def _on_refobj_destroyed(ref, self_weak=WeakProxy(self)):
			if self_weak.is_alive():
				if not self_weak.is_invalidated():
					self_weak._invalidate()
			log.verbose(utils.function.msg_kw(f"Reference {ref} has been garbage collected")) # Log after invalidating to avoid infinite recursion in log subscriptions
		return utils.function.glue(_on_refobj_destroyed, on_refobj_destroyed)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.repr_params()})"

	def __bool__(self):
		return self.is_valid()

	def repr_params(self):
		return f"callable='{self.callable}', caller='{self.cb_self}', max_calls={self.max_calls}, invalidate_on_false={self.invalidate_on_false}, args={self._args}, kwargs={self._kwargs}"

	@property
	def callable(self):
		return self.callable_ref() if self.callable_ref is not None else None
			
	@property
	def cb_self(self):
		return self.cb_self_ref() if self.cb_self_ref is not None else None

	def _invalidate(self):
		# Keep internal data unchanged for debugging purposes
		with self._invalidate_lock as acquired: # _invalidated flag can be checked through is_valid() with an assumption that the attached _on_invalidated callback was called (e.g. against existing subscriptions in notify() call to ensure subscriptions were unsubscribed in self._on_invalidated callback),
			if not acquired:
				raise RuntimeError(utils.function.msg_kw("Failed to acquire the lock to invalidate the callable"))
			# therefore the lock is needed to glue setting _invalicated flag with _on_invalidated call into an atomic operation.
			if self._invalidated:
				raise RuntimeError(utils.function.msg_kw("Callable has already been invalidated"))
			self._invalidated = True
			if self._on_invalidated is not None:
				self._on_invalidated(self)
		log.verbose(utils.function.msg_kw()) # Log after invalidating to avoid infinite recursion in log subscriptions

	# Checks the state of the callable.
	def is_valid(self):
		return not (self._invalidated or self.callable is None)

	# Checks if the callable was invalidated. Atomic with _invalidate() call.
	def is_invalidated(self):
		# with self._invalidate_lock:
		with self._invalidate_lock as acquired:
			if not acquired:
				raise RuntimeError(utils.function.msg_kw("Failed to acquire the lock in time"))
			return self._invalidated

	def _invalidate_on_ref(self, ref):
		if ref is not None:
			if ref() is None:
				self._invalidate()
				return True
		return False

	# Call operator. Returns False if the callable should be no longer valid
	def __call__(self, *args, **kwargs):
		if not self.is_valid():
			return None
		if self._invalidate_on_ref(self.callable_ref):
			log.error(f"Callable is deleted, but not unsubscribed. Invalidating the callable {self}")
			return None
		if self._invalidate_on_ref(self.cb_self_ref):
			log.error(f"Subscriber is deleted, but not unsubscribed. Invalidating the callable {self}")
			return None
		if self.max_calls is not None:
			if self._call_count >= self.max_calls:
				self._invalidate()
				# Invalidate before logging to avoid infinite recursion since there are subscriptions on logs
				log.error(f"Trying to call a callable '{self}' that has reached ({self._call_count}) its max call count {self.max_calls}, but has not unsubscribed yet for some reason. Unsubscribing it ignoring this call.")
				return None
		cb_self = self.cb_self
		all_args = list(self._args or []) + list(args)
		_args = [cb_self] + all_args if cb_self is not None else all_args
		result = self.callable(*_args, **(self._kwargs or {}), **kwargs)
		self._call_count += 1
		if self.invalidate_on_false:
			if result is False:
				log.verbose(f"Callable '{self}' returned False. Invalidating it.")
				self._invalidate()
				return result
		if self.max_calls is not None:
			if self._call_count >= self.max_calls:
				log.verbose(f"Callable '{self}' has reached its max call count {self.max_calls}. Invalidating it.")
				self._invalidate()
				return result
		return result

	def __eq__(self, other):
		if isinstance(other, Callable):
			if self.callable == other.callable:
				return True
			return False
		if not self.callable == other:
			return inspect_utils.function(other) == self.callable
		return True

class OwnedCallable(Callable):
	def __init__(self, callable, owner=None, *args, **kwargs):
		# Initialized first for repr
		_on_refobj_destroyed = self.gen_refobj_destroyed_cb()
		self.owner_ref = weakref.ref(owner, _on_refobj_destroyed) if owner is not None else None
		if self.owner_ref is not None:
			log.verbose(utils.function.msg(f"Owner weak reference {self.owner_ref} created"))
		super().__init__(callable, *args, **kwargs)

	@classmethod
	def bind_if_func(cls, callable, owner, *args, **kwargs):
		_owner = utils.lang.extract_self(callable) or owner
		return cls(callable, _owner, *args, **kwargs)

	@property
	def owner(self):
		return self.owner_ref() if self.owner_ref is not None else None

	def __call__(self, *args, **kwargs):
		if self._invalidate_on_ref(self.owner_ref):
			log.error(f"Subscriber is deleted, but not unsubscribed. Invalidating the callable {self}")
			return None
		return super().__call__(*args, **kwargs)

	def __eq__(self, other):
		result = super().__eq__(other)
		if isinstance(other, Callable):
			if result:
				owner1, owner2 = self.owner, other.owner
				if owner1 is None or owner2 is None:
					return True
				return owner1 == owner2
		return result

	def repr_params(self):
		return f"{super().repr_params()}, owner='{self.owner}'"

class SmartCallable(OwnedCallable):
	_id = -1
	_lock = wrap_debug_lock(threading.Lock())
	# Thread-safe global callback id generator

	@staticmethod
	def _next_id():
		with SmartCallable._lock:
			SmartCallable._id += 1
			return SmartCallable._id

	def __init__(self, callable, owner=None, *args, **kwargs):
		# Initialized first for repr
		self.id = self._next_id()
		super().__init__(callable, owner, *args, **kwargs)
		if owner is not None:
			# Add __smartcbs__ attribute as a list of callables to the owner if not present
			smartcbs = getattr(owner, "__smartcbs__", None)
			if smartcbs is None:
				smartcbs = OrderedDict()
				owner.__smartcbs__ = smartcbs
			cb = inspect_utils.function(callable) or callable
			if not smartcbs.add(self.id, cb):
				raise RuntimeError(utils.method.msg_kw(f"Callable is already attached to the owner"))

	def __del__(self):
		log.verbose(utils.function.msg_kw())
		owner = self.owner
		if owner is not None:
			smartcbs = getattr(owner, "__smartcbs__", None)
			if smartcbs is not None:
				owner.__smartcbs__.remove(self.id)
				log.verbose(utils.method.msg(f"Callable id={self.id} detached from the owner"))
				if len(owner.__smartcbs__) == 0:
					del owner.__smartcbs__
					log.verbose(f"__smartcbs__ attribute removed from the owner")
		utils.lang.safe_super(SmartCallable, self).__del__()

	def repr_params(self):
		return f"id={self.id}, {super().repr_params()}"

# Reminders:
# It doesn't work with super() calls since they assume self is of a type of the class where the method is defined.
class WeakProxy:
	def __init__(self, obj):
		self._ref = weakref.ref(obj)

	def __getattr__(self, name):
		obj = self._ref()
		if obj is None:
			raise ReferenceError(utils.method.msg_kw(f"Weak reference to self is no longer valid"))
		return getattr(obj, name)

	def __call__(self, *args, **kwargs):
		obj = self._ref()
		if obj is None:
			raise ReferenceError(utils.method.msg_kw("Weak reference is no longer valid"))
		return obj(*args, **kwargs)

	def __instancecheck__(self, instance):
		obj = self._ref()
		return isinstance(obj, instance)
	
	def __bool__(self):
		return self.deref() is not None

	def is_alive(self):
		return self.__bool__()

	def deref(self):
		return self._ref()
	
	def __eq__(self, other):
		return self.deref() == other


def weak_self_method(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		self_weak_wrapper = WeakProxy(self)
		return method(self_weak_wrapper, *args, **kwargs)
	return wrapper

def weak_self_class(cls):
	for attr_name, attr_value in cls.__dict__.items():
		if callable(attr_value) and not attr_name.startswith("__"):
			setattr(cls, attr_name, weak_self_method(attr_value))
	return cls

def weak_proxy(obj):
	return WeakProxy(obj)

	