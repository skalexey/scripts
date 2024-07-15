import threading
from functools import wraps
from threading import Lock, current_thread, main_thread


def thread_check(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		if not hasattr(self, 'thread'):
			raise RuntimeError(f"{self.__class__.__name__} has no attribute 'thread'. Ensure 'self.thread' is initialized in '__init__'.")
		if current_thread() not in (main_thread(), self.thread):
			raise RuntimeError(f"Method {method.__name__} can only be called from the main thread or the designated thread.")
		return method(self, *args, **kwargs)
	return wrapper

def apply_thread_check(cls):
	for attr_name, attr_value in cls.__dict__.items():
		if isinstance(attr_value, property):
			# Decorate property getter
			if not hasattr(attr_value.fget, '_allow_any_thread'):
				attr_value = attr_value.getter(thread_check(attr_value.fget))
			# Decorate property setter
			if attr_value.fset and not hasattr(attr_value.fset, '_allow_any_thread'):
				attr_value = attr_value.setter(thread_check(attr_value.fset))
			setattr(cls, attr_name, attr_value)
		elif callable(attr_value) and not hasattr(attr_value, '_allow_any_thread') and attr_name != '__init__':
			setattr(cls, attr_name, thread_check(attr_value))
	return cls


def allow_any_thread(method):
	method._allow_any_thread = True  # Flag method as excluded
	return method

def allow_any_thread_with_lock(lock_name):
	def decorator(method):
		method._allow_any_thread = True  # Flag method as excluded
		@wraps(method)
		def wrapper(self, *args, **kwargs):
			lock = getattr(self, lock_name)
			with lock:
				return method(self, *args, **kwargs)
		return wrapper
	return decorator


if __name__ == "__main__":
	from tests.test import *

	@apply_thread_check
	class A:
		def __init__(self):
			self.thread = threading.current_thread()  # Assign the current thread for demonstration
			self._lock = Lock()  # A lock for methods that need it
		
		def method_1(self):
			log("method_1 executed")
		
		@allow_any_thread
		def method_2(self):
			log("method_2 executed")
		
		@allow_any_thread_with_lock('_lock')
		def method_3(self):
			log("method_3 executed under lock")
		
		@property
		def my_property(self):
			return "property value"
		
		@my_property.setter
		def my_property(self, value):
			log(f"property set to {value}")

	def test1():
		log(title("Test 1"))

		# Example Usage:
		a = A()
		a.method_1()  # Should execute without issue
		a.method_2()  # Should execute without issue
		a.method_3()  # Should execute without issue

		# Accessing property
		log(a.my_property)
		a.my_property = "new value"

		log(title("End of Test 1"))


	def test2():
		log(title("Test 2"))

		import threading
		import unittest

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

		unittest.main()

		log(title("End of Test 2"))

	def test():
		log(title("Concurrency Decorators Test"))
		test1()
		test2()
		log(title("End of Concurrency Decorators Test"))

	run()