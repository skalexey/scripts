import random
import threading
import time
from typing import Optional

import utils.method
from utils.lang import safe_enter
from utils.live import verify
from utils.log import CombinedAddition, IndentAddition
from utils.log.logger import Logger

log = Logger()

# This class is used to acquire multiple locks at once without the risk of deadlocks using algorithm similar to the Banker's.
# Not sharable between threads. Assumed to be used in a particular moment and then destroyed.
class ScopedLock:
	def __init__(self, *locks, blocking: bool=True, timeout: Optional[float]=-1):
		super().__init__()
		# log.debug(utils.method.msg_kw())
		self.locks = sorted(locks, key=lambda x: id(x))  # Sort locks by id for consistent order
		self.acquired_locks = []
		self.timeout = timeout
		self.blocking = blocking
		self.indent_addition = IndentAddition()

	def acquire(self, blocking: bool=True, timeout: Optional[float]=-1) -> bool:
		_timeout = None if timeout < 0 else timeout
		# log.debug(utils.method.msg_kw(), addition=self.indent_addition)
		indent_block = self.indent_addition.indent_block()
		if not blocking:
			verify(_timeout is None, TypeError("Non-blocking mode does not support timeouts"))
			return self.try_acquire_all()
		if _timeout == 0:
			return self.try_acquire_all()

		start_time = time.time()
		attempt = 1
		remaining_timeout = _timeout
		while True:
			# log.debug(f"Attempt {attempt} to acquire all locks", addition=self.indent_addition)
			indent_block_2 = self.indent_addition.indent_block()
			dt = time.time() - start_time
			remaining_timeout = (_timeout - dt) if _timeout is not None else None
			if remaining_timeout is not None:
				if remaining_timeout < 0:
					if attempt > 1:
						# log.debug("Timeout reached", addition=self.indent_addition)
						self.release()
						return False
			# log.debug(f"Remaining timeout: {remaining_timeout} (dt: {dt})", addition=self.indent_addition)
			timeout_to_pass = max(0, remaining_timeout) if remaining_timeout is not None else -1
			# Try to acquire the first lock, potentially blocking if needed
			if not self.locks[0].acquire(timeout=timeout_to_pass):
				return False
			self.acquired_locks.append(self.locks[0])
			# log.debug("First lock acquired", addition=self.indent_addition)
			acquired = self.try_acquire_from(1)
			# log.debug(f"{'All locks acquired!' if acquired else 'Not acquired all locks'}", addition=self.indent_addition)
			if acquired:
				return True
			self.release()
			# If not acquired, apply a short sleep to avoid busy-waiting
			time.sleep(random.uniform(0.01, 0.1))
			attempt += 1
			del indent_block_2

	def try_acquire_all(self) -> bool:
		return self.try_acquire_from(0)

	def try_acquire_from(self, index) -> bool: # type: ignore
		for i in range(index, len(self.locks)):
			lock = self.locks[i]
			if not lock.acquire(blocking=False):
				# log.debug(f"Failed to acquire lock {i}", addition=self.indent_addition)
				self.release_back_until(index)
				return False
			self.acquired_locks.append(lock)
			# log.debug(f"Lock {i} acquired", addition=self.indent_addition)
		return True

	def release(self):
		self.release_back_until(0)

	def release_back_until(self, index):
		# log.debug(utils.method.msg_kw(f"Releasing {len(self.acquired_locks) - index} locks"), addition=self.indent_addition)
		for i in range(len(self.acquired_locks) - index):
			lock = self.acquired_locks.pop()
			lock.release()

	def locked(self) -> bool:
		return bool(self.acquired_locks)

	@safe_enter
	def __enter__(self):
		# log.debug(utils.method.msg_kw())
		self.acquire(blocking=self.blocking, timeout=self.timeout)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		# log.debug(utils.method.msg_kw())
		self.release()
