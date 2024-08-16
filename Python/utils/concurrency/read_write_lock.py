import threading


class ReadWriteLock:
	def __init__(self):
		self.readers = 0
		self.read_lock = threading.Lock()
		self.write_lock = threading.Lock()
	
	def acquire_read(self):
		with self.read_lock:
			self.readers += 1
			if self.readers == 1:
				self.write_lock.acquire()
	
	def release_read(self):
		with self.read_lock:
			self.readers -= 1
			if self.readers == 0:
				self.write_lock.release()
	
	def acquire_write(self):
		self.write_lock.acquire()
	
	def release_write(self):
		self.write_lock.release()


if __name__ == "__main__":
	# Example usage
	read_write_lock = ReadWriteLock()

	def reader_task(lock, thread_id):
		lock.acquire_read()
		print(f"Thread {thread_id} is reading")
		lock.release_read()

	def writer_task(lock, thread_id):
		lock.acquire_write()
		print(f"Thread {thread_id} is writing")
		lock.release_write()

	# Example of readers and writers
	threads = []
	for i in range(5):
		t = threading.Thread(target=reader_task, args=(read_write_lock, i))
		threads.append(t)
		t.start()

	t = threading.Thread(target=writer_task, args=(read_write_lock, 5))
	threads.append(t)
	t.start()

	for t in threads:
		t.join()
