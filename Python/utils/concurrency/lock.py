# Experimental lock implementation using threading.Event

import threading

import utils  # Lazy import for less important modules
from utils.concurrency.abstract_lock import AbstractLock


class Lock(AbstractLock):
	def __init__(self):
		self._event = threading.Event()
		self._event.set()
		self._thread_local = threading.local()

	def acquire(self, blocking=True, timeout=-1):
		if not blocking:
			if not self._event.is_set():
				return False
		if not self._event.wait(timeout): # TODO: critical section
			return False
		self._event.clear()
		self._thread_local.acquired = True
		return True
		# while True:
		# 	if self._event.is_set():
		# 		# We will use a trick with Event: clear it, then verify if it was set in a thread-safe way
		# 		self._event.clear()
		# 		if not self._event.is_set():  # If it was not set by another thread after clear() and before is_set() check
		# 			return
		# 		# If we cleared it and another thread did not set it between clear() and is_set(), we've acquired the lock
		# 		self._event.set()  # Restore the flag since we did not get the lock
		# 	self._event.wait(timeout)  # Block until the flag is set again
	
	def release(self):
		if not self.acquired():
			raise RuntimeError(utils.method.msg_kw("Lock is not acquired"))
		del self._thread_local.acquired
		self._event.set()

	def acquired(self):
		return getattr(self._thread_local, "acquired", False)

	def locked(self):
		return not self._event.is_set()
