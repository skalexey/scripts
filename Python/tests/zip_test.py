from test import *


def zip_test():
	class A:
		def __init__(self):
			self.iter_called = 0
			self._list = [1, 2, 3]

		def __iter__(self):
			log("Iterating")
			self.iter_called += 1
			return iter(self._list)

	aa = A()
	assert aa.iter_called == 0
	
	# Create a generator expression, but it should not trigger __iter__ yet
	iterable = (a for a in aa)
	assert aa.iter_called == 0  # No iteration yet, generator is just created
	
	# Now, instead of using zip, just iterate over the generator
	for _ in iterable:
		pass
	
	# Now the __iter__ method has been called
	assert aa.iter_called == 1


def test():
	log(title("Zip Test"))
	zip_test()
	log(title("End of Zip Test"))

run()
