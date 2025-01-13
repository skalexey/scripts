import inspect
import threading
from functools import wraps

from utils.class_utils import method_list
from utils.concurrency.read_write_lock import ReadWriteLock


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

def make_thread_safe_rw(obj, read_lock, write_lock, write_interface=None, no_lock_interface=None):
	"""
	Modify an object in-place to make its attributes and methods thread-safe with separate read and write locks.

	Args:
		obj: The object to be modified.
		read_lock: A lock instance for read operations.
		write_lock: A lock instance for write operations.
		write_interface: A class defining methods that require a write lock.
		no_lock_interface: A class defining methods that don't require any lock.

	Returns:
		The modified object (for convenience).
	"""
	# Create a ReadWriteLock with the provided locks
	rw_lock = ReadWriteLock(read_lock, write_lock)

	# Get write methods and no-lock methods using method_list
	write_methods = method_list(write_interface) if write_interface else []
	no_lock_methods = method_list(no_lock_interface) if no_lock_interface else []

	def wrap_method(method, lock):
		"""Wrap a method to make it thread-safe under the specified lock."""
		@wraps(method)
		def locked_method(*args, **kwargs):
			with lock:
				return method(*args, **kwargs)
		return locked_method

	# Wrap the methods of the object
	for name in dir(obj):
		attr = getattr(obj, name)

		# Ensure the attribute is a function/method and not something else
		if inspect.isfunction(attr) or inspect.ismethod(attr):
			if name in write_methods:
				# Wrap write methods with the write lock
				setattr(obj, name, wrap_method(attr, rw_lock.write))
			elif name not in no_lock_methods:
				# Wrap other methods with the read lock (exclude no-lock methods)
				setattr(obj, name, wrap_method(attr, rw_lock.read))

	# Attach the ReadWriteLock to the object
	setattr(obj, 'lock', rw_lock)

	return obj

