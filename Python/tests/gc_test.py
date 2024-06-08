import gc
from test import *

from utils.log.logger import *

log = Logger()
_globals = globals()
class D:
	def __init__(self, c):
		log(f"D('{c}')")

	def __del__(self):
		log("__del__(D)")
		
class C:
	def __init__(self):
		log("C()")
		d = D(self)

	def __del__(self):
		log("__del__(C)")

class B:
	def __init__(self, a):
		log(f"B('{a}')")
		self.a = a

	def __del__(self):
		log("__del__(B)")
		self.a = None

class A:
	def __init__(self):
		log("A()")
		self.b = B(self)

	def __del__(self):
		log("__del__(A)")
		self.b = None

def no_collect_cyclic_test():
	log(title("no_collect_cyclic_test"))
	a = A()
	a = None
	log(title("no_collect_cyclic_test end"))

def collect_cyclic_test():
	log(title("collect_cyclic_test"))
	a = A()
	log("a = None")
	a = None
	log("gc.collect()")
	gc.collect()
	log(title("collect_cyclic_test end"))

def no_collect_no_cyclic_test():
	log(title("no_collect_no_cyclic_test"))
	c = C()
	c = None
	log(title("no_collect_no_cyclic_test end"))


def test():
	no_collect_cyclic_test()
	collect_cyclic_test()
	no_collect_no_cyclic_test()

run()

