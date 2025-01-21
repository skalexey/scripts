import threading
import time

from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger

log = Logger()


class ReadWriteLock:
	def __init__(self, write_lock=None):
		"""
		Initialize the ReadWriteLock.
		Uses a Condition to synchronize readers and a Lock for writers.
		"""
		self._read_cv = threading.Condition()
		self._write_lock = threading.RLock()  # Dedicated lock for write operations
		self._reader_count = 0
		self.read = wrap_debug_lock(ParameterizedLock(self.ReadLockWrapper(self)))
		self.write = wrap_debug_lock(ParameterizedLock(self.WriteLockWrapper(self)))

	class ReadLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			start_time = time.monotonic()
			with self._rwlock._read_cv:
				while not blocking or self._rwlock.write.acquired():
					if not blocking:
						return False
					if timeout >= 0:
						remaining_time = timeout - (time.monotonic() - start_time)
						if remaining_time <= 0:
							return False
						if not self._rwlock._read_cv.wait(timeout=remaining_time):
							return False
					else:
						self._rwlock._read_cv.wait()
				self._rwlock._reader_count += 1
				return True

		def release(self):
			with self._rwlock._read_cv:
				if self._rwlock._reader_count == 0:
					raise RuntimeError("Read lock is not acquired while being released")
				self._rwlock._reader_count -= 1
				if self._rwlock._reader_count == 0:
					self._rwlock._read_cv.notify_all()  # Notify waiting writers

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			return self._rwlock._write_lock.acquire(blocking, timeout)

		def release(self):
			if not self.acquired():
				raise RuntimeError("Write lock is not acquired while being released")
			self._rwlock._write_lock.release()

		def acquired(self):
			all_attrs = dir(self)
			if "locked" in all_attrs:
				return not self.locked
			if "acquired" in all_attrs:
				return self.acquired
			if "_is_owned" in all_attrs:
				return self._is_owned()
			raise AttributeError("Read lock object has no attribute 'acquired'")

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()


if __name__ == "__main__":
	# Example usage
	rwlock = ReadWriteLock()

	def reader_task(lock, thread_id):
		with lock.read:
			print(f"Thread {thread_id} is reading")
			time.sleep(1)

	def writer_task(lock, thread_id):
		with lock.write:
			print(f"Thread {thread_id} is writing")
			time.sleep(2)

	# Example of readers and writers
	threads = []
	for i in range(3):
		t = threading.Thread(target=reader_task, args=(rwlock, i))
		threads.append(t)
		t.start()

	t = threading.Thread(target=writer_task, args=(rwlock, 3))
	threads.append(t)
	t.start()

	for t in threads:
		t.join()
