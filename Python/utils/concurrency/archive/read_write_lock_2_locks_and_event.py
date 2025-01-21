import threading
import time

from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.debug import wrap_debug_lock


class ReadWriteLock:
	def __init__(self):
		"""
		Initialize the ReadWriteLock.
		"""
		self._readers = 0
		self._writer = None  # Tracks the current thread holding the write lock
		self._write_recursion_count = 0  # Tracks recursive acquisitions by the writer
		self._write_lock = threading.Lock()
		self._read_lock = threading.Lock()
		self._writer_waiting = threading.Event()
		self._writer_waiting.clear()
		# self.read = wrap_debug_lock(ParameterizedLock(self.ReadLock(self)))
		# self.write = wrap_debug_lock(ParameterizedLock(self.WriteLock(self)))
		self.read = self.ReadLock(self)
		self.write = self.WriteLock(self)


	class ReadLock:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			# Logic to acquire the read lock
			start_time = time.time()
			while True:
				if not blocking and timeout == -1:
					if self._rwlock._writer_waiting.is_set():
						return False
					with self._rwlock._read_lock:
						self._rwlock._readers += 1
						return True

				if timeout != -1 and time.time() - start_time >= timeout:
					return False

				if not self._rwlock._writer_waiting.is_set():
					with self._rwlock._read_lock:
						self._rwlock._readers += 1
						return True

				time.sleep(0.001)

		def release(self):
			# Logic to release the read lock
			with self._rwlock._read_lock:
				if self._rwlock._readers == 0:
					raise RuntimeError("Read lock is not acquired while being released")
				self._rwlock._readers -= 1

		def __enter__(self):
			self.acquire()
			return True

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()

	class WriteLock:
		def __init__(self, rwlock):
			self._rwlock = rwlock

		def acquire(self, blocking=True, timeout=-1):
			current_thread = threading.current_thread()
			if self._rwlock._writer == current_thread:
				# Recursive acquisition
				self._rwlock._write_recursion_count += 1
				return True

			start_time = time.time()
			self._rwlock._writer_waiting.set()
			try:
				while True:
					if not blocking and timeout == -1:
						if self._rwlock._readers == 0 and self._rwlock._write_lock.acquire(False):
							self._rwlock._writer = current_thread
							self._rwlock._write_recursion_count = 1
							return True
						return False

					if timeout != -1 and time.time() - start_time >= timeout:
						return False

					if self._rwlock._readers == 0 and self._rwlock._write_lock.acquire(True):
						self._rwlock._writer = current_thread
						self._rwlock._write_recursion_count = 1
						return True

					time.sleep(0.001)
			finally:
				self._rwlock._writer_waiting.clear()

		def release(self):
			current_thread = threading.current_thread()
			if self._rwlock._writer != current_thread:
				raise RuntimeError("Write lock can only be released by the owning thread")

			self._rwlock._write_recursion_count -= 1
			if self._rwlock._write_recursion_count == 0:
				self._rwlock._writer = None
				self._rwlock._write_lock.release()

		def __enter__(self):
			self.acquire()
			return True

		def __exit__(self, exc_type, exc_value, traceback):
			self.release()


if __name__ == "__main__":
	# Example usage
	rwlock = ReadWriteLock()

	def reader_task(lock, thread_id):
		with lock.read:
			print(f"Thread {thread_id} is reading")

	def writer_task(lock, thread_id):
		with lock.write as acquired1:
			assert acquired1
			print(f"Thread {thread_id} is writing")
			with lock.write as acquired2:
				assert acquired2
				print(f"Thread {thread_id} is writing again")

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
