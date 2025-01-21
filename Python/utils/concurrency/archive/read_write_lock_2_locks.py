import threading

import utils.method
from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.log.logger import Logger

log = Logger()


class ReadWriteLock:
	def __init__(self, write_lock=None):
		"""
		Initialize the ReadWriteLock with provided write lock.
		If no locks are provided, defaults to reentrant locks (threading.RLock).

		Args:
			write_lock: A lock instance for write operations.
		"""
		self._read_lock = threading.Lock()
		self._write_lock = write_lock or threading.Lock()
		self._readers = 0  # Tracks the number of readers

		self.read = ParameterizedLock(self.ReadLockWrapper(self))
		self.write = ParameterizedLock(self.WriteLockWrapper(self))

	class ReadLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, *args, **kwargs):
			with self._rwlock._read_lock:
				self._rwlock._readers += 1
				# log.debug(utils.method.msg_kw(f"Readers now: {self._rwlock._readers}"))
				if self._rwlock._readers == 1:
					log.debug(f"Reader acquires the write lock. Readers: {self._rwlock._readers}")
					return self._rwlock._write_lock.acquire(*args, **kwargs)
				return True

		def release(self, *args, **kwargs):
			assert self._rwlock._readers >= 0, f"ReadWriteLock readers counter is unsynchronized: {self._rwlock._readers}"
			if self._rwlock._readers == 0:
				raise RuntimeError("Read lock is not acquired while being released")
			with self._rwlock._read_lock:
				self._rwlock._readers -= 1
				# log.debug(utils.method.msg_kw(f"Readers now: {self._rwlock._readers}"))
				if self._rwlock._readers == 0:
					log.debug(f"Reader releases the write lock. Readers: {self._rwlock._readers}")
					self._rwlock._write_lock.release(*args, **kwargs)

		def acquired(self):
			with self._rwlock._read_lock:
				return self._rwlock._readers > 0

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, *args, **kwargs):
			log.debug("Writer acquires the write lock")
			return self._rwlock._write_lock.acquire(*args, **kwargs)

		def release(self, *args, **kwargs):
			log.debug("Writer releases the write lock")
			self._rwlock._write_lock.release(*args, **kwargs)

		def __enter__(self):
			return self.acquire()

		def acquired(self):
			write_lock = self._rwlock._write_lock
			all_attrs = dir(write_lock)
			if "locked" in all_attrs:
				return self._rwlock._write_lock.locked()
			if "acquired" in all_attrs:
				return self._rwlock._write_lock.acquired()
			assert False, "Write lock does not have 'locked' or 'acquired' attribute"

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()


if __name__ == "__main__":
	# Example usage
	rwlock = ReadWriteLock()

	def reader_task(lock, thread_id):
		with lock.read:
			print(f"Thread {thread_id} is reading")

	def writer_task(lock, thread_id):
		with lock.write:
			print(f"Thread {thread_id} is writing")

	# Example of readers and writers
	threads = []
	for i in range(5):
		t = threading.Thread(target=reader_task, args=(rwlock, i))
		threads.append(t)
		t.start()

	t = threading.Thread(target=writer_task, args=(rwlock, 5))
	threads.append(t)
	t.start()

	for t in threads:
		t.join()