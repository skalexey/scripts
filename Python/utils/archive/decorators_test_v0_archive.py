import threading
import unittest

from utils.concurrency.decorators import (
    allow_any_thread,
    allow_any_thread_with_lock,
    apply_thread_check,
)


@apply_thread_check
class A:
	def __init__(self):
		self.thread = threading.current_thread()  # Assign the current thread for demonstration
		self._lock = threading.Lock()  # A lock for methods that need it
	
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

class TestThreadCheck(unittest.TestCase):
	def setUp(self):
		self.a = A()
	
	def test_method_1_in_main_thread(self):
		self.a.method_1()  # Should not raise any exception
	
	def test_method_1_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.method_1()
			self.assertIn("Method method_1 can only be called from the main thread or the designated thread.", str(context.exception))
		
		t = threading.Thread(target=target)
		t.start()
		t.join()

	def test_method_2_in_any_thread(self):
		def target():
			try:
				self.a.method_2()  # Should not raise any exception
				executed = True
			except RuntimeError:
				executed = False
			self.assertTrue(executed)

		t = threading.Thread(target=target)
		t.start()
		t.join()
	
	def test_method_3_in_any_thread_with_lock(self):
		def target():
			try:
				self.a.method_3()  # Should not raise any exception
				executed = True
			except RuntimeError:
				executed = False
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
			self.assertIn("can only be called from the main thread or the designated thread.", str(context.exception))

		t = threading.Thread(target=target)
		t.start()
		t.join()
	
	def test_my_property_setter_in_main_thread(self):
		self.a.my_property = "new value"  # Should not raise any exception
	
	def test_my_property_setter_in_wrong_thread(self):
		def target():
			with self.assertRaises(RuntimeError) as context:
				self.a.my_property = "new value"
			self.assertIn("can only be called from the main thread or the designated thread.", str(context.exception))

		t = threading.Thread(target=target)
		t.start()
		t.join()

if __name__ == '__main__':
	unittest.main()
