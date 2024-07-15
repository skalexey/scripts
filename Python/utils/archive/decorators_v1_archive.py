import threading
from functools import wraps
from threading import Lock, current_thread, main_thread

# Decorators

def thread_check(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		if not hasattr(self, 'thread'):
			raise RuntimeError(f"{self.__class__.__name__} has no attribute 'thread'. Ensure 'self.thread' is initialized in '__init__'.")
		if current_thread() not in (main_thread(), self.thread):
			raise RuntimeError(f"Method {method.__name__} can only be called from the main thread or the designated thread.")
		return method(self, *args, **kwargs)
	return wrapper

def allow_any_thread(method):
	method._allow_any_thread = True  # Flag method as excluded
	return method

def allow_any_thread_with_lock(lock_name):
	def decorator(method):
		method._allow_any_thread = True  # Flag method as excluded
		@wraps(method)
		def wrapper(self, *args, **kwargs):
			lock = getattr(self, lock_name)
			with lock:
				return method(self, *args, **kwargs)
		return wrapper
	return decorator

# Mixin Class

class ThreadGuard:
	def __setattr__(self, name, value):
		if not name.startswith('_') and not hasattr(self, '_init_completed'):
			object.__setattr__(self, name, value)
		elif name == 'thread':
			object.__setattr__(self, name, value)
		else:
			if current_thread() not in (main_thread(), self.thread):
				raise RuntimeError(f"Attribute {name} can only be set from the main thread or the designated thread.")
			object.__setattr__(self, name, value)

	def __getattribute__(self, name):
		if name == 'thread' or name.startswith('_'):
			return object.__getattribute__(self, name)
		method = object.__getattribute__(self, name)
		if getattr(method, '_allow_any_thread', None):
			return method
		if current_thread() not in (main_thread(), object.__getattribute__(self, 'thread')):
			raise RuntimeError(f"Attribute {name} can only be accessed from the main thread or the designated thread.")
		return method

	def __delattr__(self, name):
		if current_thread() not in (main_thread(), self.thread):
			raise RuntimeError(f"Attribute {name} can only be deleted from the main thread or the designated thread.")
		object.__delattr__(self, name)

	def __init__(self):
		self._init_completed = True  # Flag to allow setting initial attributes


