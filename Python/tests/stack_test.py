import inspect
from test import *

import utils.function
import utils.inspect_utils as inspect_utils


def class_in_locals_test():
	log(title("Class in Locals Test"))
	class A:
		def __init__(self):
			frame = inspect.currentframe()
			log(utils.function.msg(f"frame locals: {frame.f_locals}"))

		def f(self):
			frame = inspect.currentframe()
			log(utils.function.msg(f"frame locals: {frame.f_locals}"))

	class B(A):
		def __init__(self):
			frame = inspect.currentframe()
			log(utils.function.msg(f"frame locals: {frame.f_locals}"))
			super().__init__()

		def f(self):
			frame = inspect.currentframe()
			log(utils.function.msg(f"frame locals: {frame.f_locals}"))
			super().f()

	b = B()
	log(title("End of Class in Locals Test"))

def class_of_function_test():
	import inspect

	def get_class_that_defined_method(method):
		"""Return the class that defined the given method."""
		if hasattr(method, '__self__'):
			# Bound method
			if inspect.isclass(method.__self__):
				method_class = method.__self__
			else:
				method_class = method.__self__.__class__
			for cls in inspect.getmro(method_class):
				me = cls.__dict__.get(method.__name__)
				if me is not None:
					if inspect.isfunction(me):
						func = me
					elif inspect.ismethod(me):
						func = me.__func__
					else:
						func = me.__func__
					if func is method.__func__:
						if func.__code__ is method.__func__.__code__:  # This check is necessary to avoid false positives
							return cls
					return cls
			method = method.__func__  # Unbind the method for the next part

		if hasattr(method, '__qualname__'):
			cls_name = method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0]
			try:
				cls = getattr(inspect.getmodule(method), cls_name)
				if isinstance(cls, type):
					return cls
			except AttributeError:
				pass
		return None

	def get_class_that_called_function():
		stack = inspect.stack()
		for frame_info in stack[1:]:  # Skip current and caller frame
			frame = frame_info.frame
			# Check if it's a method of a class instance or a class itself
			if 'self' in frame.f_locals:
				instance = frame.f_locals['self']
				method_name = frame.f_code.co_name
				method = getattr(instance, method_name, None)
				if method:
					cls = get_class_that_defined_method(method)
					if cls:
						return cls
			elif 'cls' in frame.f_locals:
				cls = frame.f_locals['cls']
				method_name = frame.f_code.co_name
				method = getattr(cls, method_name, None)
				if method:
					cls = get_class_that_defined_method(method)
					if cls:
						return cls
		return None

	# Example usage
	class A:
		def instance_method(self):
			print(get_class_that_called_function())

		@classmethod
		def class_method(cls):
			print(get_class_that_called_function())

	class B(A):
		def instance_method(self):
			super().instance_method()

		@classmethod
		def class_method(cls):
			print(get_class_that_called_function())

	class C(B):
		pass

	# Calling methods to test
	c = C()
	c.instance_method()
	C.class_method()  
	B.class_method()
	A.class_method()
	

def test():
	log(title("Stack Test"))
	# class_in_locals_test()
	class_of_function_test()
	log(title("End of Stack Test"))

run()