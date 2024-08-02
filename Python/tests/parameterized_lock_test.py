import unittest
from test import *
from threading import Lock, RLock, Thread
from unittest.mock import Mock, patch

from utils.concurrency.parameterized_lock import ParameterizedLock

# from parameterized_context_manager_test import TestParameterizedContextManager


class TestParameterizedLock(unittest.TestCase):
	def setUp(self):
		self.lock = Lock()
		self.context_manager = ParameterizedLock(self.lock)

	@timeout(1)
	def test_on_enter_result(self):
		with self.context_manager() as state:
			self.assertTrue(state.acquired())

	@timeout(1)
	def test_acquire_and_release_lock(self):
		with self.context_manager():
			self.assertTrue(self.context_manager.acquired())
			self.assertTrue(self.lock.locked())
		self.assertFalse(self.lock.locked())
		self.assertFalse(self.context_manager.acquired())

	@timeout(1)
	def test_constant_args(self):
		self.lock.acquire()
		self.context_manager.set_constant_args(timeout=0.3)
		with self.context_manager:
			self.assertFalse(self.context_manager.acquired())
		self.context_manager.reset_constant_args()
		self.assertFalse(self.context_manager.acquired())
		# Release the lock after the test
		self.lock.release()

	@timeout(1)
	def test_failed_non_blocking_enter(self):
		# Acquire the lock manually to force the context manager to fail
		self.lock.acquire()
		with self.context_manager(blocking=False):
			self.assertFalse(self.context_manager.acquired())
		self.assertFalse(self.context_manager.acquired())
		# Release the lock after the test
		self.lock.release()

	@timeout(1)
	def test_failed_timedout_enter(self):
		# Acquire the lock manually to force the context manager to fail
		self.lock.acquire()
		with self.context_manager(timeout=0.3):
			self.assertFalse(self.context_manager.acquired())
		self.assertFalse(self.context_manager.acquired())
		# Release the lock after the test
		self.lock.release()

	@timeout(1)
	def test_failed_enter_with_exception(self):
		# Acquire the lock manually to force the context manager to fail
		self.context_manager = ParameterizedLock(self.lock, except_on_timeout=True)
		self.lock.acquire()
		with self.assertRaises(RuntimeError) as tc:
			with self.context_manager(timeout=0.3):
				self.assertTrue(False) # Should be never reached
		self.assertEqual(str(tc.exception), "Failed to acquire the lock in time")
		self.assertFalse(self.context_manager.acquired())
		# Release the lock after the test
		self.lock.release()

	@timeout(1)
	def test_failed_enter_with_exception_noargs(self):
		# Acquire the lock manually to force the context manager to fail
		self.context_manager = ParameterizedLock(self.lock, except_on_timeout=True)
		self.context_manager.set_constant_args(timeout=0.3)
		self.lock.acquire()
		with self.assertRaises(RuntimeError) as tc:
			with self.context_manager:
				self.assertTrue(False) # Should be never reached
		self.assertEqual(str(tc.exception), "Failed to acquire the lock in time")
		self.assertFalse(self.context_manager.acquired())
		# Release the lock after the test
		self.lock.release()

	@timeout(1)
	def test_failed_enter_with_custom_exception(self):
		# Acquire the lock manually to force the context manager to fail
		self.lock.acquire()
		self.context_manager = ParameterizedLock(self.lock, except_on_timeout=RuntimeError("Failed to acquire the lock"))
		with self.assertRaises(RuntimeError) as tc:
			with self.context_manager(timeout=0.3):
				self.assertFalse(self.context_manager.acquired())
		self.assertEqual(str(tc.exception), "Failed to acquire the lock")
		self.assertFalse(self.context_manager.acquired())
		# Release the lock after the test
		self.lock.release()

	@timeout(1)
	def test_exception(self):
		try:
			with self.context_manager():
				self.assertTrue(self.context_manager.acquired())
				self.assertTrue(self.lock.locked())
				raise RuntimeError("Test exception")
		except RuntimeError as e:
			self.assertIn("Test exception", str(e))
			self.assertFalse(self.context_manager.acquired())
			self.assertFalse(self.lock.locked())

class TestParameterizedLockRLock(unittest.TestCase):
	def setUp(self):
		self.lock = RLock()
		self.context_manager = ParameterizedLock(self.lock)
		
		def thread1_job():
			pass

		def thread2_job():
			pass

		self.thread1_job = thread1_job
		self.thread2_job = thread2_job
		self.thread1 = Thread(target=self.thread1_job, name="Thread1")
		self.thread2 = Thread(target=self.thread2_job, name="Thread2")

	@timeout(1)
	def test_on_enter_result(self):
		with self.context_manager() as state:
			self.assertTrue(state.acquired())

	@timeout(1)
	def test_acquire_and_release_lock(self):
		with self.context_manager():
			self.assertTrue(self.context_manager.acquired())
			self.assertTrue(self.lock._is_owned())
			with self.context_manager():
				self.assertTrue(self.context_manager.acquired())
				self.assertTrue(self.lock._is_owned())
		self.assertFalse(self.lock._is_owned())
		self.assertFalse(self.context_manager.acquired())

def parameterized_lock_test():
	unittest.main()

def test():
	log(title("Parameterized Lock Test"))
	parameterized_lock_test()
	log(title("End of Parameterized Lock Test"))

run()
