import random
import threading

import utils.concurrency.lock
from utils.concurrency.nodeadlock import NoDeadLock

from tests.test import *


class RandomLock(utils.concurrency.lock.Lock):
	def acquire(self, blocking=True, timeout=-1):
		return super().acquire(blocking=True, timeout=random.uniform(0.001, 0.1))

lock1 = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()
custom_lock = RandomLock()
locks = [lock1, lock2, lock2]

def safe_function(blocking, timeout):
	random.shuffle(locks)
	locked_count = 0
	with NoDeadLock(*locks, blocking=blocking, timeout=timeout) as ndl:
		locked_count = len(ndl.acquired_locks)
		if ndl.locked():
			log("All locks acquired")
			for lock in locks:
				assert lock.locked(), "Locks should be locked when NoDeadLock is acquired"
		else:
			log(f"Failed to acquire all locks in {'non' if not blocking else ''} blocking mode after timeout {timeout}")
			assert len(locks) != locked_count, "Some locks should be acquired when NoDeadLock failed to acquire all locks"
		# Perform operations while holding all locks
		sleep(random.uniform(0.001, 0.01))  # Simulate very short work
	log(f"{locked_count} locks released")

def small_test(blocking, timeout):
	log(title("NoDeadLock Small Test"))
	for lock in locks:
		assert not lock.locked(), "Locks should not be acquired at the beginning of the test"
	safe_function(blocking, timeout)
	for lock in locks:
		assert not lock.locked(), "Locks should not be acquired at the end of the test"
	log(title("End of NoDeadLock Small Test"))

def load_test(iterations, blocking, timeout):
	log(title("Load Test"))
	# Load test
	def job(iterations):
		for i in range(iterations):
			log(f"Load test iteration {i}")
			safe_function(blocking, timeout)

	# Example threads that use the NoDeadLock with random lock order
	threads = [threading.Thread(target=job, args=(iterations,)) for _ in range(10)]
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	
	log(title("End of Load Test"))


def nodeadlock_test():
	log(title("Nodeadlock Test"))
	small_test(blocking=True, timeout=0.5)
	with AssertException(TypeError("Non-blocking mode does not support timeouts")):
		small_test(blocking=False, timeout=0.3)
	# load_test(100, blocking=False, timeout=-1)
	load_test(100, blocking=True, timeout=0)
	load_test(100, blocking=False, timeout=-1)
	load_test(100, blocking=True, timeout=0.1)
	load_test(100, blocking=True, timeout=-1)

def test():
	log(title("Start Tests"))
	for i in range(100):
		log(f"Nodeadlock Test iteration {i}")
		nodeadlock_test()
	nodeadlock_test()
	log(title("All Tests completed"))

run()
