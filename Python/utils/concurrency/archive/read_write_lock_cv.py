import threading
import time

import utils.method
from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger

log = Logger()

class ReadWriteLock:
	def __init__(self):
		"""
		Initialize the ReadWriteLock.
		Uses a Condition to synchronize access between readers and writers.
		"""
		self._lock = threading.Condition()
		self._reader_count = 0
		self._writer_active = False
		self._write_owner = None  # Tracks which thread owns the write lock
		self._write_recursion_count = 0  # Tracks the recursion depth of the write lock
		# self.read = wrap_debug_lock(ParameterizedLock(self.ReadLockWrapper(self)))
		# self.write = wrap_debug_lock(ParameterizedLock(self.WriteLockWrapper(self)))
		self.read = ParameterizedLock(self.ReadLockWrapper(self))
		self.write = ParameterizedLock(self.WriteLockWrapper(self))

	class ReadLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			start_time = time.monotonic()
			with self._rwlock._lock:
				while self._rwlock._writer_active and self._rwlock._write_owner != threading.get_ident():
					if not blocking:
						return False
					if timeout >= 0:
						remaining_time = timeout - (time.monotonic() - start_time)
						if remaining_time <= 0:
							return False
						if not self._rwlock._lock.wait(timeout=remaining_time):
							return False
					else:
						self._rwlock._lock.wait()
				self._rwlock._reader_count += 1
				return True

		def release(self):
			with self._rwlock._lock:
				if self._rwlock._reader_count == 0:
					raise RuntimeError("Read lock is not acquired while being released")
				self._rwlock._reader_count -= 1
				if self._rwlock._reader_count == 0:
					self._rwlock._lock.notify_all()  # Notify writers waiting for access

		def __enter__(self):
			return self.acquire()

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLockWrapper:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			start_time = time.monotonic()
			with self._rwlock._lock:
				current_thread_id = threading.get_ident()
				# Allow reentrant locking for the same thread
				if self._rwlock._writer_active and self._rwlock._write_owner == current_thread_id:
					self._rwlock._write_recursion_count += 1
					return True
				# Wait until no readers or writers are active
				while self._rwlock._reader_count > 0 or self._rwlock._writer_active:
					if not blocking:
						return False
					if timeout >= 0:
						remaining_time = timeout - (time.monotonic() - start_time)
						if remaining_time <= 0:
							return False
						if not self._rwlock._lock.wait(timeout=remaining_time):
							return False
					else:
						self._rwlock._lock.wait()
				# Acquire the write lock
				self._rwlock._writer_active = True
				self._rwlock._write_owner = current_thread_id
				self._rwlock._write_recursion_count = 1
				return True

		def release(self):
			with self._rwlock._lock:
				if not self._rwlock._writer_active or self._rwlock._write_owner != threading.get_ident():
					raise RuntimeError("Write lock is not acquired by this thread or is already released")
				# Decrement recursion count
				self._rwlock._write_recursion_count -= 1
				if self._rwlock._write_recursion_count == 0:
					# Fully release the write lock
					self._rwlock._writer_active = False
					self._rwlock._write_owner = None
					self._rwlock._lock.notify_all()  # Notify readers and writers waiting for access

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

	def writer_task(lock, thread_id):
		with lock.write:
			print(f"Thread {thread_id} is writing")
			# Reentrant behavior
			with lock.write:
				print(f"Thread {thread_id} is recursively writing")

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
