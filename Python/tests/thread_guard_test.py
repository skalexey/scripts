import threading
import unittest

import utils.method
from utils.concurrency.thread_guard import (
    ThreadGuard,
    allow_any_thread,
    allow_any_thread_with_lock,
)
from utils.log.logger import Logger

log = Logger()
# Class Definition for Testing
class A(ThreadGuard):
	def __init__(self):
		super().__init__()
		self.thread1 = threading.current_thread()  # Assign the current thread for demonstration
		self.thread2 = threading.Thread(target=lambda: None)  # Another thread for demonstration
		self.lock = threading.Lock()  # A lock for methods that need it
		self.some_attr = "Initial value"

	@property
	def my_property(self):
		return self.some_attr

	@my_property.setter
	def my_property(self, value):
		self.some_attr = value
		log(f"Property set to {value}")

	def method_1(self):
		log("method_1 executed")

	@allow_any_thread
	def method_2(self):
		log("method_1 executed")

	@allow_any_thread_with_lock('lock')
	def method_3(self):
		log("method_3 executed under lock")

class B(A):
	@allow_any_thread
	def allowed_method(self):
		log("allowed_method_1 executed")

	def not_allowed_method(self):
		log("not_allowed_method executed")

class TestThreadCheck(unittest.TestCase):
	def setUp(self):
		self.a = A()
		self.a.allow_thread(threading.main_thread())

	def test_method_1_in_main_thread(self):
		self.a.method_1()  # Should not raise any exception

	def test_method_1_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.method_1()
			log(f"Exception message: {str(context.exception)}")
			self.assertIn("can only be called", str(context.exception))
		thread = threading.Thread(target=target)
		thread.start()
		thread.join()

	def test_method_2_in_any_thread(self):
		def target():
			try:
				self.a.method_3()  # Should not raise any exception
				executed = True
			except RuntimeError as e:
				executed = False
				log(f"Exception message: {str(e)}")
			self.assertTrue(executed)
		thread = threading.Thread(target=target)
		thread.start()
		thread.join()

	def test_attribute_access_in_main_thread(self):
		self.a.some_attr = "New value"  # Should not raise any exception
		log(self.a.some_attr)  # Should not raise any exception

	def test_attribute_access_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.some_attr = "New value"
			log(f"Exception message: {str(context.exception)}")
			self.assertIn("Method '__setattr__' can only be called from any of allowed threads", str(context.exception))
		thread = threading.Thread(target=target)
		thread.start()
		thread.join()

	def test_allow_any_thread_with_lock_in_any_thread(self):
		def target():
			try:
				self.a.method_3()  # Should not raise any exception
				executed = True
			except RuntimeError as e:
				executed = False
				log(f"Exception message: {str(e)}")
			self.assertTrue(executed)
		thread = threading.Thread(target=target)
		thread.start()
		thread.join()

	def test_get_attr(self):
		log(utils.method.msg_kw(f"Attr value: {self.a.some_attr}"))

	def test_hasattr(self):
		self.assertTrue(hasattr(self.a, 'some_attr'))
		self.assertFalse(hasattr(self.a, 'undefined_attr'))

	def test_get_attr_not_exist(self):
		with self.assertRaises(AttributeError) as context:
			log(utils.method.msg_kw(f"Attr value: {self.a.unefined_attr}"))
		log(f"Exception message: {str(context.exception)}")
		self.assertIn("no attribute", str(context.exception))

	def test_get_attr_other_thread(self):
		def target():
			log(utils.method.msg_kw(f"Attr value: {self.a.some_attr}"))
		thread = threading.Thread(target=target)
		thread.start()
		thread.join()

if __name__ == '__main__':
	unittest.main()
