
from collections import defaultdict
from functools import wraps
from threading import current_thread

# from utils.log.logger import Logger

# log = Logger()
# log.redirect_to_file(postfix='_thread_guard')


class ThreadControl:
	def __init__(self, obj):
		self._obj = obj

	def __enter__(self):
		self._obj._tmp_thread_ids[current_thread().name] += 1
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		enter_level = self._obj._tmp_thread_ids[current_thread().name]
		if enter_level == 1:
			del self._obj._tmp_thread_ids[current_thread().name]
		else:
			self._obj._tmp_thread_ids[current_thread().name] -= 1

def allow_any_thread(method_func):
	@wraps(method_func)
	def wrapper(self, *args, **kwargs):
		with ThreadControl(self): # Allow consequitive depth accesses once an allowed method is reached
			return method_func(self, *args, **kwargs)
	wrapper._allow_any_thread = True
	return wrapper

def allow_any_thread_with_lock(lock_name):
	def decorator(method_func):
		@wraps(method_func)
		def wrapper(self, *args, **kwargs):
			lock = getattr(self, lock_name)
			with lock:
				return method_func(self, *args, **kwargs)
		return allow_any_thread(wrapper)
	return decorator

def is_lock(value):
	return hasattr(value, '__enter__')

def is_thread(value):
	return hasattr(value, 'ident')

def thread_check(method_func):
	@wraps(method_func)
	def wrapper(self, *args, **kwargs):
		# log.verbose(f"Checking thread access for thread '{current_thread().name}' to method '{method_func.__name__}'")
		if not self._is_thread_allowed(current_thread()):
			raise RuntimeError(f"Method '{method_func.__name__}' can only be called from any of allowed threads: {self._allowed_thread_ids}. Current thread: '{current_thread().name}'")
		# log.verbose(f"	Thread access granted for method '{method_func.__name__}'")
		return method_func(self, *args, **kwargs)
	return wrapper


def apply_thread_check(cls):
	for attr_name, attr_value in cls.__dict__.items():
		if isinstance(attr_value, property):
			# Decorate property getter
			func = attr_value.fget
			if not hasattr(func, '_allow_any_thread'):
				attr_value = attr_value.getter(thread_check(func))
			# Decorate property setter
			func = attr_value.fset
			if func and not hasattr(func, '_allow_any_thread'):
				attr_value = attr_value.setter(thread_check(func))
			setattr(cls, attr_name, attr_value)
		elif callable(attr_value) and not hasattr(attr_value, '_allow_any_thread') and attr_name != '__init__' and attr_name != '_is_thread_allowed':
			setattr(cls, attr_name, thread_check(attr_value))
	return cls

# ThreadGuard class allows to restrict methods, properties, and writing access to only specific threads.
# Access for reading to existing attributes is always allowed. It is quite cumbersome to override __getattribute__ and is not needed in 99% of cases.
@apply_thread_check
class ThreadGuard:
	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		apply_thread_check(cls)
		
	def __init__(self, *args, **kwargs):
		super().__setattr__('_tmp_thread_ids', defaultdict(int))
		super().__setattr__('_allowed_thread_ids', set([current_thread().name]))
		super().__init__(*args, **kwargs)

	def allow_thread(self, thread):
		self._allowed_thread_ids.add(thread.name)

	def __setattr__(self, name, value):
		if is_thread(value):
			self.allow_thread(value)
		super().__setattr__(name, value)

	def _is_thread_allowed(self, thread):
		return thread.name in self._allowed_thread_ids or thread.name in self._tmp_thread_ids
	