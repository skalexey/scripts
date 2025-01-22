import threading


class RSemaphore:
	def __init__(self, value=1):
		"""
		Initialize the RSemaphore with a given initial value.
		:param value: The initial value of the semaphore (default: 1).
		"""
		self._semaphore = threading.Semaphore(value)
		self._local = threading.local()

	@property
	def _acquired_count(self):
		"""
		Thread-local property to get the acquire count.
		"""
		return getattr(self._local, "count", 0)

	@_acquired_count.setter
	def _acquired_count(self, value):
		self._local.count = value

	def acquire(self, *args, **kwargs):
		"""
		Acquire the semaphore, incrementing the local count if successful.
		Propagates additional arguments to the underlying semaphore's acquire method.
		:return: True if the semaphore was acquired, False otherwise.
		"""
		if self._acquired_count == 0:
			if not self._semaphore.acquire(*args, **kwargs):
				return False
		self._acquired_count += 1
		return True

	def release(self):
		"""
		Release the semaphore, decrementing the local count.
		"""
		if self._acquired_count > 0:
			self._acquired_count -= 1
			if self._acquired_count == 0:
				self._semaphore.release()
		else:
			raise RuntimeError("Cannot release an unacquired semaphore")

	def count(self):
		"""
		Get the current count of acquires for this thread.
		:return: The count of acquires.
		"""
		return self._acquired_count

	def __enter__(self):
		"""
		Enter the runtime context, acquiring the semaphore.
		:return: True if the semaphore was acquired, False otherwise.
		"""
		return self.acquire()

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Exit the runtime context, releasing the semaphore.
		"""
		self.release()
