import threading

import utils.method
from utils.concurrency import lock_owner
from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.context import GlobalContext
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger

log = Logger()


def get_thread_full_descriptor(thread):
	return f"{thread.name} ({thread.ident})"


class ReadWriteLock:
	def __init__(self):
		"""
		Initialize the ReadWriteLock with provided write lock.
		If no locks are provided, defaults to reentrant locks (threading.RLock).

		Args:
			write_lock: A lock instance for write operations.
		"""
		self._want_write_event = threading.Event()
		self.read = wrap_debug_lock(ParameterizedLock(self.ReadLock(self)))
		self.write = wrap_debug_lock(ParameterizedLock(self.WriteLock(self)))
		self._write_owner = None



	class Lock:
		def __init__(self, rwlock):
			self._rwlock = rwlock
			self._tloc = threading.local()
			self._owner = None

		@property
		def _acquired_count(self):
			return self._tloc.acquired_count if hasattr(self._tloc, "acquired_count") else 0
		
		@_acquired_count.setter
		def _acquired_count(self, value):
			self._tloc.acquired_count = value


	class ReadLock(Lock):
		def __init__(self, rwlock):
			super().__init__(rwlock)
			self._lock = wrap_debug_lock(ParameterizedLock(threading.Lock()))
			self._readers = 0  # Tracks the number of readers
			self._readers_lock = threading.Lock()

		def acquire(self, *args, **kwargs):
			with self._lock(*args, **kwargs):
				self._owner = threading.current_thread()
				# log.debug(utils.method.msg_kw(f"Readers now: {self._readers}"))
				log.debug(f"Reader acquires the read lock. Readers: {self._readers}. Current reader owner: {self._rwlock.read._owner}. Current writing owner: {self._rwlock.write._owner}")
				if self._readers == 0:
					assert self._rwlock.write._acquired_count == 0, f"Read lock is acquired while write lock is acquired for writing"
					log.debug(f"Reader acquires the write lock. Readers: {self._readers}. Current reader owner: {self._rwlock.read._owner}. Current writing owner: {self._rwlock.write._owner}")
					result = self._rwlock.write._acquire_lock(*args, **kwargs)
					if not result:
						return False
					# assert not self._rwlock._want_write_event.is_set(), "Read lock is acquired while write lock is requested for writing"
				else:
					if self._rwlock._want_write_event.is_set():
						blocking = args[0] if args else kwargs.get("blocking", True)
						timeout = args[1] if len(args) > 1 else kwargs.get("timeout", -1)
						if not blocking:
							return False
						start_time = GlobalContext.current_time()
						result = self._rwlock._want_write_event.wait(timeout)
						if not result:
							return False
						else:
							elapsed = GlobalContext.current_time() - start_time
							remaining = timeout - elapsed
							if remaining <= 0:
								return False
							result = self._rwlock.write._acquire_lock(blocking, remaining)
							if not result:
								return False
				with self._readers_lock:
					self._readers += 1
				self._acquired_count += 1
				return True

		def release(self, *args, **kwargs):
			assert self._readers >= 0, f"ReadWriteLock readers counter is unsynchronized: {self._readers}"
			if self._readers == 0:
				raise RuntimeError("Read lock is not acquired while being released")
			assert self._acquired_count > 0, f"Read lock is released while it is being acquired {self._acquired_count} times"
			self._acquired_count -= 1
			with self._readers_lock:
				self._readers -= 1
				log.debug(f"Reader releases the read lock. Readers: {self._readers}")
				# log.debug(utils.method.msg_kw(f"Readers now: {self._readers}"))
				if self._readers == 0:
					log.debug(f"    Reader releases the write lock. Readers: {self._readers}")
					# TODO: Support this assert: assert self._rwlock.write._owner is None, f"Read lock is released while write lock is acquired for writing"
					self._rwlock.write._release_lock(*args, **kwargs)
					self._owner = None

		def acquired(self):
			with self._lock:
				return self._readers > 0

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLock(Lock):
		def __init__(self, rwlock):
			super().__init__(rwlock)
			self._lock = wrap_debug_lock(ParameterizedLock(threading.Lock()))

		def acquire(self, *args, **kwargs):
			log.debug(f"Writer acquires the write lock. Acquired count: {self._acquired_count}")
			if self._acquired_count == 0:
				self._rwlock._want_write_event.set()
				result = self._acquire_lock(*args, **kwargs)  # TODO: check the case with several writers waiting and then changing the event state. What is the resulting state?
				self._rwlock._want_write_event.clear()
				return result
			else:
				self._acquired_count += 1
				return True

		def release(self, *args, **kwargs):
			log.debug(f"Writer releases the write lock. Acquired count: {self._acquired_count}")
			self._release_lock(*args, **kwargs)

		def __enter__(self):
			return self.acquire()

		def acquired(self):
			write_lock = self._lock
			all_attrs = dir(write_lock)
			if "locked" in all_attrs:
				return self._lock.locked()
			if "acquired" in all_attrs:
				return self._lock.acquired()
			assert False, "Write lock does not have 'locked' or 'acquired' attribute"

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

		def _acquire_lock(self, *args, **kwargs):
			read = self._rwlock.read
			log.debug(utils.method.msg_kw(f"readers: {read._readers}, read.acquired_count: {read._acquired_count}"))
			if read._acquired_count == 0:
				result = self._lock.acquire(*args, **kwargs)
			else:  # If we are reading, the write lock is acquired and we can be the last reader
				result = True
			if result:
				self._acquired_count += 1
				self._write_owner = threading.current_thread()
				log.debug(f"Write lock acquired by {get_thread_full_descriptor(threading.current_thread())}. Acquired count: {self._acquired_count}")
			return result
		
		def _release_lock(self, *args, **kwargs):
			log.debug(f"Releasing write lock by {get_thread_full_descriptor(threading.current_thread())}. Acquired count: {self._acquired_count}")
			if self._acquired_count > 0:
				self._acquired_count -= 1
			if self._acquired_count == 0:
				self._lock.release(*args, **kwargs)
				log.debug(f"Write lock released by {get_thread_full_descriptor(threading.current_thread())}. Acquired count: {self._acquired_count}")
				self._write_owner = None


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