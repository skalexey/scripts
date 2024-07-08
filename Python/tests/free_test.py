from test import *


def extend_test():
	l1 = [1,2]
	l2 = [2,3]
	l1.extend(l2)
	print(l1)
	print([1,2].extend([2,3]))


def set_test():
	def add_test():
		s1 = set({1,2,3})
		s2 = set()
		for key in s1:
			s2.add(key)
		print(s2)

	def pop_test():
		s = set({1,2,3})
		print(s.pop())
		print(s.pop())
		print(s.pop())
		print(s.pop())
		print(s.pop())
		print(s.pop())
	pop_test()

def dict_test():
	def update_test():
		d1 = {1:2, 2:3}
		d2 = {2:4, 3:5}
		d1.update(d2)
		print(d1)
		e2 = d1.pop(2)
		e4 = d1.get(4)
		print(e4)
		e4 = d1.pop(4)
		print(e4)
		print(e2)

	def pop_test():
		def pop(d, key, default=...):
			return d.pop(key, default)
		def pop2(d, key, *args):
			return d.pop(key, *args)
		def pop_test_impl(pop_func):
			d = {1:2, 2:3}
			print(pop_func(d, 1, 0))
			print(pop_func(d, 3, 0))
			try:
				print(pop_func(d, 4))
			except KeyError as e:
				print(e)

		def pop_empty_default():
			d = {}
			print(d.pop(1, 44))
			print(d.pop(1))

		pop_test_impl(pop)
		pop_test_impl(pop2)
		pop_empty_default()


def partial_test():
	from functools import partial

	def original_function(first_arg, second_arg):
		return f"First argument: {first_arg}, Second argument: {second_arg}"

	# Create a partial function that always adds the second argument
	second_argument = "fixed_value"
	partial_function = partial(original_function, second_argument)

	# Use the partial function
	result = partial_function("dynamic_value")
	print(result)  # Output: "First argument: dynamic_value, Second argument: fixed_value"

partial_test()

def get_prop_method_test():
	class MyClass:
		def __init__(self, value):
			self._value = value

		@property
		def value(self):
			return self._value

	# Create an instance of the class
	obj = MyClass(42)

	# Access the property's getter method directly and bind it to the instance
	getter_method = MyClass.value.__get__(obj)

	# Call the getter method
	print(getter_method())  # Output: 42

def mro_test():
	class M:
		pass

	log(M.mro())

def test():
	mro_test()

run()
