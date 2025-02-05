import inspect
import multiprocessing
import threading
from collections import defaultdict
from functools import wraps


class ContextControl:
	def __init__(self, obj, context_getter):
		self._obj = obj
		self._context_getter = context_getter

	def __enter__(self):
		context_id = self._context_getter().name
		self._obj._tmp_context_ids[context_id] += 1
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		context_id = self._context_getter().name
		enter_level = self._obj._tmp_context_ids[context_id]
		if enter_level == 1:
			del self._obj._tmp_context_ids[context_id]
		else:
			self._obj._tmp_context_ids[context_id] -= 1

def allow_any_context(method_func):
	"""
	Decorator to allow a method to be called from any thread or process.
	"""
	@wraps(method_func)
	def wrapper(self, *args, **kwargs):
		with ContextControl(self, self._context_getter):
			return method_func(self, *args, **kwargs)
	wrapper._allow_any_context = True
	return wrapper

def allow_any_context_with_lock(lock_name):
	"""
	Decorator to allow a method under a specified lock.
	"""
	def decorator(method_func):
		@wraps(method_func)
		def wrapper(self, *args, **kwargs):
			lock = getattr(self, lock_name)
			with lock:
				return method_func(self, *args, **kwargs)
		return allow_any_context(wrapper)
	return decorator

def is_lock(value):
	return hasattr(value, '__enter__')

def is_thread(value):
	return isinstance(value, threading.Thread)

def is_process(value):
	return isinstance(value, multiprocessing.Process)

def context_check(method_func, cls):
	@wraps(method_func)
	def wrapper(self, *args, **kwargs):
		cls = self.__class__
		context_id = cls._context_getter().name
		if not self._is_context_allowed(context_id):
			raise RuntimeError(
				f"Method '{cls.__name__}.{method_func.__name__}' can only be called from allowed contexts: {self._allowed_context_ids}. Current context: '{context_id}'"
			)
		return method_func(self, *args, **kwargs)
	return wrapper

def apply_context_check(cls):
	for attr_name, attr_value in cls.__dict__.items():
		if isinstance(attr_value, property):
			func = attr_value.fget
			if not hasattr(func, '_allow_any_context'):
				attr_value = attr_value.getter(context_check(func, cls))
			func = attr_value.fset
			if func and not hasattr(func, '_allow_any_context'):
				attr_value = attr_value.setter(context_check(func, cls))
			setattr(cls, attr_name, attr_value)
		elif inspect.isfunction(attr_value) and not hasattr(attr_value, '_allow_any_context') and attr_name != '__init__' and attr_name != '_is_context_allowed' and attr_name != '_context_getter':
			setattr(cls, attr_name, context_check(attr_value, cls))
	return cls

@apply_context_check
class ContextGuard:
	"""
	Base guard class that allows restricting method access based on the execution context (thread or process).
	"""
	_context_getter = None
	
	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		apply_context_check(cls)

	def __init__(self, *args, **kwargs):
		assert self._context_getter is not None, "Derived class must define '_context_getter' class attribute"
		super().__setattr__('_tmp_context_ids', defaultdict(int))
		super().__setattr__('_allowed_context_ids', set([self.__class__._context_getter().name]))
		super().__init__(*args, **kwargs)

	def allow_context(self, context):
		self._allowed_context_ids.add(context.name)

	def allow_context_name(self, context_name):
		self._allowed_context_ids.add(context_name)

	def __setattr__(self, name, value):
		if is_thread(value) or is_process(value):
			self.allow_context(value)
		super().__setattr__(name, value)

	def _is_context_allowed(self, context_id):
		return context_id in self._allowed_context_ids or context_id in self._tmp_context_ids
