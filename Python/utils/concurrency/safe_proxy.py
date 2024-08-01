import threading
from functools import wraps


class SafeProxy:
	def __init__(self, obj):
		super().__setattr__('_obj', obj)
		super().__setattr__('_lock', threading.Lock())
		super().__setattr__('_methods', {})
		super().__setattr__('_attributes', {})
		self._wrap_methods()

	def _wrap_methods(self):
		for name in dir(self._obj):
			if not name.startswith("_") or name == "__setattr__":
				attr = getattr(self._obj, name)
				if callable(attr):
					wrapped_method = self._create_locked_method(attr)
					self._methods[name] = wrapped_method
				else:
					self._attributes[name] = attr

	def _create_locked_method(self, method):
		@wraps(method)
		def locked_method(*args, **kwargs):
			with self._lock:
				return method(*args, **kwargs)
		return locked_method

	def __getattr__(self, name):
		# Check in wrapped methods first
		if name in self._methods:
			return self._methods[name]
		# Check in attributes
		if name in self._attributes:
			return self._attributes[name]
		# Fallback to the wrapped object
		return getattr(self._obj, name)

	def __setattr__(self, name, value):
		if name in ('_obj', '_lock', '_methods', '_attributes'):
			super().__setattr__(name, value)
		else:
			with self._lock:
				setattr(self._obj, name, value)
	