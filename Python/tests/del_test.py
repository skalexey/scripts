from test import *

from utils.ordered_dict import *
from utils.subscription import *


class A:
	def __init__(self):
		log("A.__init__")
		self.b_list = OrderedDict()
		self.sub = Subscription()
		for i in range(10):
			self.b_list[i] = B(self)
		self.sub.subscribe(self.f)

	def f(self):
		log("A.f()")

	def __del__(self):
		log("A.__del__")
		self.sub = None

class B:
	def __init__(self, a):
		log("B.__init__")
		# self.a = a
		self.sub = Subscription()
		# self.sub.subscribe(a.sub)

	def __del__(self):
		log("B.__del__")

class C:
	def __init__(self):
		log("C.__init__")
		self.a = A()

	def __del__(self):
		log("C.__del__")

def test():
	log(title("__del__ test"))
	c = C()
	c.a = A()
	log(title("End of __del__ test"))
run()