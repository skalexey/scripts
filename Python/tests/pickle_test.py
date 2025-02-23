import pickle
from test import *


class A:
	def __init__(self, x):
		self.x = x

def pickle_test():
	log(title("Pickle Test"))

	# Let's see how pickle digests circular reference
	a = A(None)
	b = A(a)
	a.x = b
	pickled = pickle.dumps(a)
	log(title("End of Pickle Test"))

def test():
	pickle_test()

run()
