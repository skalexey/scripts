import threading
import unittest

from utils.concurrency.thread_guard import (
    ThreadGuard,
    allow_any_thread,
    allow_any_thread_with_lock,
)


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
		print(f"Property set to {value}")

	def method_1(self):
		print("method_1 executed")

	@allow_any_thread
	def method_2(self):
		print("method_1 executed")

	@allow_any_thread_with_lock('lock')
	def method_3(self):
		print("method_3 executed under lock")

class TestThreadCheck(unittest.TestCase):
	def setUp(self):
		self.a = A()

	def test_method_1_in_main_thread(self):
		self.a.method_1()  # Should not raise any exception

	def test_method_1_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.method_1()
			print(f"Exception message: ", str(context.exception))
			self.assertIn("Attribute method_1 can only be accessed from the creator thread or one of the designated threads.", str(context.exception))
		t = threading.Thread(target=target)
		t.start()
		t.join()

	def test_method_2_in_any_thread(self):
		def target():
			try:
				self.a.method_3()  # Should not raise any exception
				executed = True
			except RuntimeError as e:
				executed = False
				print(f"Exception message: {str(e)}")
			self.assertTrue(executed)
		t = threading.Thread(target=target)
		t.start()
		t.join()

	def test_attribute_access_in_main_thread(self):
		self.a.some_attr = "New value"  # Should not raise any exception
		print(self.a.some_attr)  # Should not raise any exception

	def test_attribute_access_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.some_attr = "New value"
			print(f"Exception message: ", str(context.exception))
			self.assertIn("Attribute some_attr can only be set from the creator thread or one of the designated threads.", str(context.exception))
		t = threading.Thread(target=target)
		t.start()
		t.join()

	def test_allow_any_thread_with_lock_in_any_thread(self):
		def target():
			try:
				self.a.method_3()  # Should not raise any exception
				executed = True
			except RuntimeError as e:
				executed = False
				print(f"Exception message: {str(e)}")
			self.assertTrue(executed)
		t = threading.Thread(target=target)
		t.start()
		t.join()

if __name__ == '__main__':
	unittest.main()
