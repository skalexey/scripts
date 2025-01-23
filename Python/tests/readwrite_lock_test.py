import threading

import utils.function
from utils.application_context import ApplicationContext
from utils.concurrency.read_write_lock import ReadWriteLock
from utils.log import add_global_addition
from utils.log.logger import Logger, LogLevel
from utils.pyside.application import Application

# from test import *
from utils.text import title

log = Logger()

class TestApplication(Application):
	def on_update(self, dt):
		pass

app_context = ApplicationContext()
app = TestApplication(app_context, [])
app_context.app = app

class LogAddition:
	def __str__(self):
		return f"[{threading.current_thread().name}] "

add_global_addition(LogAddition(), front=True)


def readwrite_lock_simple_test():
	lock = ReadWriteLock()
	with lock.read as acquired:
		log(f"Read lock acquired: {acquired}")

def readwrite_lock_multithread_test(thread_count=10, readonly=False):
	lock = ReadWriteLock()
	threads = []

	def read():
		with lock.read as acquired:
			log(f"Read lock acquired: {acquired}")
		log(f"Read lock released")

	def write():
		with lock.write as acquired:
			log(f"Write lock acquired: {acquired}")
			threading.Event().wait(0.1)  # Simulate write operation
		log(f"Write lock released")

	for i in range(thread_count):
		if readonly or i < thread_count * 0.3 or i > thread_count * 0.6:
			target = read
		else:
			target = write
		thread = threading.Thread(target=target)
		threads.append(thread)
		thread.start()
	for thread in threads:
		thread.join()

# The same thread writes while reading. Other threads read.
def readwrite_lock_multithread_write_while_reading_test(thread_count=10, readwrite_factor_from=0.3, readwrite_factor_to=0.6):
	log(title("Readwrite Lock Multithread Write While Reading Test"))
	lock = ReadWriteLock()
	threads = []

	def read():
		log(utils.function.msg_kw())
		with lock.read as acquired:
			log(f"Read lock acquired: {acquired}")
			threading.Event().wait(0.1)  # Simulate read operation
		log(f"Read lock released")

	def readwrite():
		log(utils.function.msg_kw())
		with lock.read as acquired_read:
			log(f"Read lock acquired: {acquired_read}")
			with lock.write as acquired_write:
				log(f"Write lock acquired: {acquired_write}")
				threading.Event().wait(0.1)  # Simulate write operation
			log(f"Write lock released") 
		log(f"Read lock released")

	for i in range(thread_count):
		if i < thread_count * readwrite_factor_from or i > thread_count * readwrite_factor_to:
			target = read
		else:
			target = readwrite
		thread = threading.Thread(target=target)
		threads.append(thread)
		thread.start()
	for thread in threads:
		thread.join()

	log(title("End of Readwrite Lock Multithread Write While Reading Test"))

def test1(read_thread_count):
	log(title("Test 1"))
	rwlock = ReadWriteLock()

	def reader_task(lock, thread_id):
		log(f"+++ Thread is reading +++")
		with lock.read:
			threading.Event().wait(0.07)
		log(f"+++ Thread has done reading +++")

	def writer_task(lock, thread_id):
		log(f"+++ Thread is writing +++")
		with lock.write:
			threading.Event().wait(0.13)
		log(f"+++ Thread has done writing +++")

	# Example of readers and writers
	threads = []
	for i in range(read_thread_count):
		t = threading.Thread(target=reader_task, args=(rwlock, i))
		threads.append(t)
		t.start()

	t = threading.Thread(target=writer_task, args=(rwlock, 5))
	threads.append(t)
	t.start()

	for t in threads:
		t.join()

	log(title("End of Test 1"))

def readwrite_lock_test():
	# readwrite_lock_simple_test()
	# for _ in range(200):
	log(title("Readwrite Lock Test"))
	# readwrite_lock_multithread_test(4)
	for i in range(111):
		log(title(f"Iteration {i}"))
		# test1(5)
		# readwrite_lock_multithread_write_while_reading_test(3, 0.33, 1)
		readwrite_lock_multithread_write_while_reading_test(10)
		log(title(f"End of Iteration {i}"))
	log(title("End of Readwrite Lock Test"))


def test():
	readwrite_lock_test()

# run()
readwrite_lock_test()
