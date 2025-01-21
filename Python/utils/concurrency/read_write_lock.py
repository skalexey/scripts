import threading

from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.context import GlobalContext
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger

log = Logger()

import threading


class ReadWriteLock:
	def __init__(self):
		"""Initialize the ReadWriteLock."""
		self._condition = threading.Condition(threading.RLock())
		self._readers = 0
		self._writer = None  # Tracks the current writer thread
		self._write_requests = 0
		self.read = wrap_debug_lock(ParameterizedLock(self.ReadLockWrapper(self)))
		self.write = wrap_debug_lock(ParameterizedLock(self.WriteLockWrapper(self)))

	class ReadLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			with self._rwlock._condition:
				log.debug(f"Read lock acquire: blocking={blocking}, timeout={timeout}")
				if not blocking and self._rwlock._write_requests > 0:
					return False

				if timeout == -1:
					while self._rwlock._write_requests > 0 or self._rwlock._writer:
						self._rwlock._condition.wait()
				else:
					start_time = GlobalContext.current_time()
					while self._rwlock._write_requests > 0 or self._rwlock._writer:
						elapsed = GlobalContext.current_time() - start_time
						remaining = timeout - elapsed
						if remaining < 0:
							return False
						self._rwlock._condition.wait(remaining)
				self._rwlock._readers += 1
				log.debug("Read lock acquired")
				return True

		def release(self):
			with self._rwlock._condition:
				log.debug("Read lock release. Readers: %d" % self._rwlock._readers)
				if self._rwlock._readers == 0:
					raise RuntimeError("Read lock released too many times")
				self._rwlock._readers -= 1
				if self._rwlock._readers == 0:
					self._rwlock._condition.notify_all()
					log.debug("Read lock released")

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.release()

	class WriteLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			with self._rwlock._condition:
				current_thread = threading.current_thread()
				if self._rwlock._writer == current_thread:
					return True  # Recursive acquisition allowed for writers

				self._rwlock._write_requests += 1

				if not blocking and (self._rwlock._readers > 0 or self._rwlock._writer):
					self._rwlock._write_requests -= 1
					return False

				if timeout == -1:
					while self._rwlock._readers > 0 or self._rwlock._writer:
						self._rwlock._condition.wait()
				else:
					start_time = GlobalContext.current_time()
					while self._rwlock._readers > 0 or self._rwlock._writer:
						elapsed = GlobalContext.current_time() - start_time
						remaining = timeout - elapsed
						if remaining <= 0:
							self._rwlock._write_requests -= 1
							return False
						self._rwlock._condition.wait(remaining)
						log.debug("Write lock acquired")

				self._rwlock._write_requests -= 1
				self._rwlock._writer = current_thread
				return True

		def release(self):
			with self._rwlock._condition:
				log.debug("Write lock release")
				if self._rwlock._writer != threading.current_thread():
					raise RuntimeError("Write lock can only be released by the acquiring thread")

				self._rwlock._writer = None
				self._rwlock._condition.notify_all()
				log.debug("Write lock released")

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_val, exc_tb):
			self.release()


# Example usage
if __name__ == "__main__":
	rwlock = ReadWriteLock()

	def reader_task(lock, thread_id):
		with lock.read:
			print(f"Thread {thread_id} is reading")

	def writer_task(lock, thread_id):
		with lock.write:
			print(f"Thread {thread_id} is writing")

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
