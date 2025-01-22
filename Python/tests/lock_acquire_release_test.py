import threading

from utils.concurrency.read_write_lock import ReadWriteLock
from utils.log import add_global_addition
from utils.log.logger import Logger

# from test import *
from utils.text import title

log = Logger()


class LogAddition:
	def __str__(self):
		return f"[{threading.current_thread().name}] "

add_global_addition(LogAddition(), front=True)

def lock_acquire_release_test():
	log(title("Lock Acquire Release Test"))
	import threading

	lock = threading.RLock()

	def thread1():
		print("Thread 1 acquiring the lock")
		lock.acquire()
		print("Thread 1 acquired the lock")

	def thread2():
		print("Thread 2 attempting to release the lock")
		lock.release()

	# Start thread 1 and acquire the lock
	t1 = threading.Thread(target=thread1)
	t1.start()
	t1.join()

	# Start thread 2 and attempt to release the lock
	t2 = threading.Thread(target=thread2)
	t2.start()
	t2.join()
	log(title("End of Lock Acquire Release Test"))


def test():
	lock_acquire_release_test()
	

lock_acquire_release_test()
