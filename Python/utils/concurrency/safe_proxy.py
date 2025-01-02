import threading
from functools import wraps

from utils.lang import safe_enter


class SafeProxy:
	def __init__(self, obj, lock=None):
		super().__setattr__('_obj', obj)
		super().__setattr__('lock', threading.Lock() if lock is None else lock)
		super().__setattr__('_methods', {})
		self._wrap_methods()

	def _wrap_methods(self):
		for name in dir(self._obj):
			if not name.startswith("_") or name == "__setattr__":
				attr = getattr(self._obj, name)
				if callable(attr):
					wrapped_method = self._create_locked_method(attr)
					self._methods[name] = wrapped_method

	def _create_locked_method(self, method):
		@wraps(method)
		def locked_method(*args, **kwargs):
			with self.lock:
				return method(*args, **kwargs)
		return locked_method

	def __getattr__(self, name):
		# Check in wrapped methods first
		if name in self._methods:
			return self._methods[name]
		# Fallback to the wrapped object
		return getattr(self._obj, name)

	def __setattr__(self, name, value):
		if name in ('_obj', 'lock', '_methods'):
			super().__setattr__(name, value)
		else:
			with self.lock:
				setattr(self._obj, name, value)

	# Non-blocking reads
	def __len__(self):
		return len(self._obj)

	def __getitem__(self, key):
		return self._obj[key]
	
	def __bool__(self):
		return bool(self._obj)

	# Additional interface
	def update(self, new_obj):
		with self.lock:
			self._obj = new_obj
			return new_obj
