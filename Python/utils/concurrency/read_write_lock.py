import threading

from utils.concurrency.parameterized_lock import ParameterizedLock


class ReadWriteLock:
	def __init__(self, read_lock=None, write_lock=None):
		"""
		Initialize the ReadWriteLock with provided read and write locks.
		If no locks are provided, defaults to reentrant locks (threading.RLock).

		Args:
			read_lock: A lock instance for read operations.
			write_lock: A lock instance for write operations.
		"""
		self._read_lock = read_lock or threading.RLock()
		self._write_lock = write_lock or threading.RLock()
		self._readers = 0  # Tracks the number of readers

		self.read = ParameterizedLock(self.ReadLockWrapper(self))
		self.write = ParameterizedLock(self.WriteLockWrapper(self))

	class ReadLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, *args, **kwargs):
			with self._rwlock._read_lock:
				self._rwlock._readers += 1
				if self._rwlock._readers == 1:
					self._rwlock._write_lock.acquire(*args, **kwargs)

		def release(self, *args, **kwargs):
			with self._rwlock._read_lock:
				self._rwlock._readers -= 1
				if self._rwlock._readers == 0:
					self._rwlock._write_lock.release(*args, **kwargs)

		def __enter__(self):
			self.acquire()
			return self

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, *args, **kwargs):
			self._rwlock._write_lock.acquire(*args, **kwargs)

		def release(self, *args, **kwargs):
			self._rwlock._write_lock.release(*args, **kwargs)

		def __enter__(self):
			self.acquire()
			return self

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
