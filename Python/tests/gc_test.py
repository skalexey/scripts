import gc
from test import *

import utils.method
from utils.log.logger import Logger
from utils.profile.refmanager import RefManager
from utils.profile.trackable_resource import TrackableResource

log = Logger()
_globals = globals()

class E(TrackableResource):
	def __init__(self):
		super().__init__()

class D(TrackableResource):
	def __init__(self, c):
		super().__init__()
		log(utils.method.msg_v())

class C(TrackableResource):
	def __init__(self):
		super().__init__()
		d = D(self)

class B(TrackableResource):
	def __init__(self, a):
		super().__init__()
		log(utils.method.msg_v())
		self.a = a

class A(TrackableResource):
	def __init__(self):
		super().__init__()
		self.b = B(self)

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

def dictionaries_test():
	log(title("Dictionaries Test"))
	e = E()
	d = {}
	d["e"] = e
	e.d = d
	b = B(e)
	log(title("End of Dictionaries Test"))

def circular_ref_test():
	log(title("Circular Reference Test"))
	# Don't use log.expr since it exposes objects to another stack frame and undermines the outcome of this test
	e = E()
	a = A()

	man = RefManager()

	def inner_scope():
		class F(E):
			def create_closure(self):
				def f():
					log(utils.method.msg_v(f"capturing self: {self}"))
				return f

			def capture_self(self):
				return self.create_closure()

			def __init__(self):
				super().__init__()
				log(utils.method.msg_v())
				self.capture_self()

		class G(F):
			def capture_self(self):
				self.f = super().capture_self()
				return self.f

		class H(F):
			def create_closure(self):
				l = lambda: log(utils.method.msg_v(f"capturing self: {self}"))
				return l

		class I(H, G):
			pass

		man.f = F()
		man.g = G()
		man.h = H()
		man.i = I()

	inner_scope()
	assert man.f is None, "F should have been collected since the function that has a reference to self captured in a closure has been collected"
	assert man.g is not None, "G should have not been collected since it has a reference to itself captured in a closure"
	assert man.h is None, "H should have been collected since the lambda that has a reference to self captured in a closure has been collected"
	assert man.i is not None, "I should have not been collected since it has a reference to itself captured in a lambda"
	log(title("End of Circular Reference Test"))

def test():
	log(title("Test"))
	# no_collect_cyclic_test()
	# collect_cyclic_test()
	# no_collect_no_cyclic_test()
	# dictionaries_test()
	circular_ref_test()
	log(title("End of Test"))

run()

