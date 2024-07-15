import threading
import unittest

from utils.concurrency.decorators import (
    ThreadGuard,
    allow_any_thread,
    allow_any_thread_with_lock,
    thread_check,
)

# Class Definition for Testing

class A(ThreadGuard):
	def __init__(self):
		self.thread = threading.current_thread()  # Assign the current thread for demonstration
		self._lock = threading.Lock()  # A lock for methods that need it
		self.some_attr = "Initial value"
		super().__init__()

	def method_1(self):
		print("method_1 executed")
	
	@allow_any_thread
	def method_2(self):
		print("method_2 executed")
	
	@allow_any_thread_with_lock('_lock')
	def method_3(self):
		print("method_3 executed under lock")
	
	@property
	def my_property(self):
		return "property value"
	
	@my_property.setter
	def my_property(self, value):
		print(f"property set to {value}")

# Test Script

class TestThreadCheck(unittest.TestCase):
	def setUp(self):
		self.a = A()
	
	def test_method_1_in_main_thread(self):
		self.a.method_1()  # Should not raise any exception
	
	def test_method_1_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.method_1()
			print("Exception message:", str(context.exception))
			self.assertIn("Attribute method_1 can only be accessed from the main thread or the designated thread.", str(context.exception))
		
		t = threading.Thread(target=target)
		t.start()
		t.join()

	def test_method_2_in_any_thread(self):
		def target():
			try:
				self.a.method_2()  # Should not raise any exception
				executed = True
			except RuntimeError as e:
				executed = False
				print("Exception message:", str(e))
			self.assertTrue(executed)

		t = threading.Thread(target=target)
		t.start()
		t.join()
	
	def test_method_3_in_any_thread_with_lock(self):
		def target():
			try:
				self.a.method_3()  # Should not raise any exception
				executed = True
			except RuntimeError as e:
				executed = False
				print("Exception message:", str(e))
			self.assertTrue(executed)

		t = threading.Thread(target=target)
		t.start()
		t.join()
	
	def test_my_property_in_main_thread(self):
		print(self.a.my_property)  # Should not raise any exception
	
	def test_my_property_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				print(self.a.my_property)
			print("Exception message:", str(context.exception))
			self.assertIn("Attribute my_property can only be accessed from the main thread or the designated thread.", str(context.exception))

		t = threading.Thread(target=target)
		t.start()
		t.join()
	
	def test_my_property_setter_in_main_thread(self):
		self.a.my_property = "new value"  # Should not raise any exception
	
	def test_my_property_setter_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.my_property = "new value"
			print("Exception message:", str(context.exception))
			self.assertIn("Attribute my_property can only be set from the main thread or the designated thread.", str(context.exception))

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
			print("Exception message:", str(context.exception))
			self.assertIn("Attribute some_attr can only be set from the main thread or the designated thread.", str(context.exception))

		t = threading.Thread(target=target)
		t.start()
		t.join()

		def target_get():
			with self.assertRaises(RuntimeError) as context:
				print(self.a.some_attr)
			print("Exception message:", str(context.exception))
			self.assertIn("Attribute some_attr can only be accessed from the main thread or the designated thread.", str(context.exception))

		t = threading.Thread(target=target_get)
		t.start()
		t.join()

if __name__ == '__main__':
	unittest.main()
