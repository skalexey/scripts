from functools import wraps
from threading import current_thread, main_thread

import utils.log
from utils.log.logger import Logger

# log = Logger()
# utils.log.redirect_to_file()

def allow_any_thread(method):
	method._allow_any_thread = True
	return method

def allow_any_thread_with_lock(lock_name):
	def decorator(method):
		@wraps(method)
		def wrapper(self, *args, **kwargs):
			lock = getattr(self, lock_name)
			with lock:
				return method(self, *args, **kwargs)
		wrapper._allow_any_thread = True
		return wrapper
	return decorator

def is_lock(value):
	return hasattr(value, '__enter__')

def is_thread(value):
	return hasattr(value, 'ident')

class ThreadGuard:
	reserved_attributes = {'_allowed_attributes', '_init_completed', '_thread_attributes', '_lock_attributes', '_creator_thread_id', '__dict__', '__class__'}
	def __init__(self, *args, **kwargs):
		self._creator_thread_id = current_thread().name # TODO: Not in use at the momoent
		self._thread_attributes = set()
		self._lock_attributes = set()
		self._allowed_attributes = set()
		self._init_completed = True
		super().__init__(*args, **kwargs)

	def __setattr__(self, name, value):
		init_completed = getattr(self, '_init_completed', None)
		if not init_completed:# or name in {'_thread_attributes', '_init_completed', '_locks'}:
			super().__setattr__(name, value)
		else:
			allowed_attributes = getattr(self, '_allowed_attributes')
			if name in allowed_attributes:
				super().__setattr__(name, value)
				return
			thread = current_thread()
			creator_thread_id = getattr(self, '_creator_thread_id')
			if thread.ident != creator_thread_id and thread.name != creator_thread_id:
				thread_attributes = getattr(self, '_thread_attributes')
				current_threads = [getattr(self, attr) for attr in thread_attributes]
				if current_thread() not in current_threads:
					print(f"Thread: {thread.name}, Creator: {creator_thread_id}, Current: {current_thread().name}")
					raise RuntimeError(f"Attribute {name} can only be set from the creator thread or one of the designated threads.")
			if is_lock(value):
				self._lock_attributes.add(name)
			elif is_thread(value):
				self._thread_attributes.add(name)
			super().__setattr__(name, value)

	def __getattribute__(self, name):
		# print(f"Getting attribute {name}")
		if name == '_init_completed':
			return self.__dict__.get(name, None)
		# if name.startswith('__') and name.endswith('__'):
		# 	return super().__getattribute__(name)
		if name in ThreadGuard.reserved_attributes:
			return super().__getattribute__(name)
		lock_attributes = getattr(self, '_lock_attributes')
		if name in lock_attributes:
			return super().__getattribute__(name)
		allowed_attributes = getattr(self, '_allowed_attributes')
		if name in allowed_attributes:
			return super().__getattribute__(name)
		thread_attributes = getattr(self, '_thread_attributes')
		if name in thread_attributes:
			return super().__getattribute__(name)
		attr = super().__getattribute__(name)
		if hasattr(attr, '_allow_any_thread'):
			return attr
		thread = current_thread()
		creator_thread_id = getattr(self, '_creator_thread_id')
		if thread.name == creator_thread_id or thread.ident == creator_thread_id:
			return attr
		current_threads = [getattr(self, attr_name) for attr_name in thread_attributes]
		if current_thread() in current_threads:
			return attr
		raise RuntimeError(f"Attribute {name} can only be accessed from the creator thread or one of the designated threads.")
