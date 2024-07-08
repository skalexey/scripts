from test import *

import utils.lang
import utils.method
from utils.collection.ordered_dict import OrderedDict
from utils.subscription import Subscription


def simple_test():
	log(title("simple_test"))
	class A:
		def __init__(self):
			log(utils.method.msg_kw())
			self.b_list = OrderedDict()
			self.sub = Subscription()
			for i in range(10):
				self.b_list[i] = B(self)
			self.sub.subscribe(self.f)

		def f(self):
			log(utils.method.msg_kw())

		def __del__(self):
			log(utils.method.msg_kw())
			self.sub = None

	class B:
		def __init__(self, a):
			log(utils.method.msg_kw())
			# self.a = a
			self.sub = Subscription()
			# self.sub.subscribe(a.sub)

		def __del__(self):
			log(utils.method.msg_kw())

	class C:
		def __init__(self):
			log(utils.method.msg_kw())
			self.a = A()

		def __del__(self):
			log(utils.method.msg_kw())

	c = C()
	c.a = A()
	log(title("End of simple_test"))

def inheritance_test():
	log(title("inheritance_test"))
	class A:
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

		def __del__(self):
			log(utils.method.msg_kw())
			utils.lang.safe_super(A, self).__del__()

	class B:
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

		def __del__(self):
			log(utils.method.msg_kw())
			utils.lang.safe_super(B, self).__del__()

	class C(A):
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

		# def __del__(self):
		# 	log(utils.method.msg_kw())
		# 	super().__del__()

	class D(B):
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

		def __del__(self):
			log(utils.method.msg_kw())
			utils.lang.safe_super(D, self).__del__()
			

	class E(C, D):
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

		def __del__(self):
			log(utils.method.msg_kw())
			# super().__del__()
			utils.lang.safe_super(E, self).__del__()

	e = E()

	log(title("End of inheritance_test"))


def test():
	log(title("__del__ test"))
	# simple_test()
	inheritance_test()
	# safe_del_test()
	log(title("End of __del__ test"))
run()