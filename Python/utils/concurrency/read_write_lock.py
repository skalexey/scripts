import threading

import utils.method
from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.concurrency.rsemaphore import RSemaphore
from utils.log.logger import Logger

log = Logger()


class ReadWriteLock:
	def __init__(self):
		"""
		Initialize the ReadWriteLock with provided write lock.
		If no locks are provided, defaults to reentrant locks (threading.RLock).

		Args:
			write_lock: A lock instance for write operations.
		"""
		self._read_lock = threading.RLock()
		self._reader_cv = threading.Condition()
		self._readers_lock = threading.RLock()
		self._write_lock = RSemaphore()
		self._readers = 0  # Tracks the number of readers

		self.read = ParameterizedLock(self.ReadLockWrapper(self))
		self.write = ParameterizedLock(self.WriteLockWrapper(self))

	class ReadLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock
			self._tloc = threading.local()
			
		@property
		def _acquired_count(self):
			return getattr(self._tloc, "acquired_count", 0)
		
		@_acquired_count.setter
		def _acquired_count(self, value):
			self._tloc.acquired_count = value

		def acquire(self, *args, **kwargs):
			with self._rwlock._read_lock:
				with self._rwlock._readers_lock:
					# log.debug(utils.method.msg_kw(f"Readers now: {self._rwlock._readers}"))
					if self._rwlock._readers == 0:
						log.debug(f"Reader acquires the write lock. Readers: {self._rwlock._readers}")
						if not self._rwlock._write_lock.acquire(*args, **kwargs):
							return False
						self._rwlock._readers += 1
						self._acquired_count += 1
						self._rwlock._write_lock.release()
					else:
						self._rwlock._readers += 1
						self._acquired_count += 1
					return True

		def release(self, *args, **kwargs):
			assert self._rwlock._readers >= 0, f"ReadWriteLock readers counter is unsynchronized: {self._rwlock._readers}"
			if self._rwlock._readers == 0:
				raise RuntimeError("Read lock is not acquired while being released")
			with self._rwlock._readers_lock:
				self._rwlock._readers -= 1
				self._acquired_count -= 1
				with self._rwlock._reader_cv:
					self._rwlock._reader_cv.notify_all()
				# log.debug(utils.method.msg_kw(f"Readers now: {self._rwlock._readers}"))
				if self._rwlock._readers == 0:
					log.debug(f"Reader releases the write lock. Readers: {self._rwlock._readers}")
					self._rwlock._write_lock.release(*args, **kwargs)

		def acquired(self):
			with self._rwlock._readers_lock:
				return self._rwlock._readers > 0

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, *args, **kwargs):
			log.debug("Writer acquires the read lock")
			if not self._rwlock._read_lock.acquire(*args, **kwargs):
				return False
			with self._rwlock._reader_cv:
				self._rwlock._reader_cv.wait_for(lambda: self._rwlock._readers == self._rwlock.read._acquired_count)
			log.debug(f"Writer acquires the write lock. Readers: {self._rwlock._readers}")
			# if self._rwlock._readers > 0:
			# 	return True
			return self._rwlock._write_lock.acquire(*args, **kwargs)

		def release(self, *args, **kwargs):
			log.debug("Writer releases the write lock")
			# if self._rwlock._readers > 0:
			# 	return 
			self._rwlock._write_lock.release(*args, **kwargs)
			log.debug("Writer releases the read lock")
			self._rwlock._readers_lock.release(*args, **kwargs)

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