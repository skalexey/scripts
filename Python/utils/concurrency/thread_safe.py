import threading
from functools import wraps


def make_thread_safe(obj, lock=None):
	"""
	Modify an object in-place to make its attributes and methods thread-safe.

	Args:
		obj: The object to be modified.
		lock: An optional threading.Lock instance. If None, a new lock will be created.

	Returns:
		The modified object (for convenience).
	"""
	if lock is None:
		lock = threading.Lock()

	def wrap_method(method):
		"""Wrap a method to make it thread-safe."""
		@wraps(method)
		def locked_method(*args, **kwargs):
			with lock:
				return method(*args, **kwargs)
		return locked_method

	# Wrap the methods of the object
	for name in dir(obj):
		if not name.startswith("_") or name == "__setattr__":
			attr = getattr(obj, name)
			if callable(attr):
				setattr(obj, name, wrap_method(attr))

	# Make the lock accessible as obj.lock
	setattr(obj, 'lock', lock)

	return obj
