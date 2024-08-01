from test import *

import utils.method
from utils.proxy import Proxy


def property_test():
	def test1():
		log(title("Test 1"))
		class A:
			def __init__(self):
				self._a = 0
				self._wobj = "WOBJ!"

			@property
			def a(self):
				log(utils.method.msg_kw())
				return self._a
			
			@a.setter
			def a(self, value):
				log(utils.method.msg_kw())
				self._a = value

			@property
			def _obj(self):
				return self._wobj
			
			@_obj.setter
			def _obj(self, value):
				self._wobj = value

		class B(A):
			def __init__(self):
				super().__init__()

			@A.a.getter
			def a(self):
				log(utils.method.msg_kw())
				return self._a
			
			@A.a.setter
			def a(self, value):
				log(utils.method.msg_kw())
				self._a = value

			@A._obj.getter
			def _obj(self):
				log(utils.method.msg_kw())
				return self._wobj
			
			@A._obj.setter
			def _obj(self, value):
				log(utils.method.msg_kw())
				self._wobj = value


		class C(B):
			def __init__(self):
				super().__init__()

			@B.a.getter
			def a(self):
				log(utils.method.msg_kw())
				return self._a
			
			@B.a.setter
			def a(self, value):
				log(utils.method.msg_kw())
				self._a = value

		b = B()
		assert b.a == 0
		b.a = 1
		assert b.a == 1

		c = C()
		assert c._obj == "WOBJ!"
		log(title("End of Test 1"))

	def test2():
		class A:
			def __init__(self, a=None, b=None):
				self.a = a
				self.b = b


			def f(self):
				log(utils.method.msg_kw(f"a={self.a}"))
				return self.a

		class WeaklyAllocated(Proxy):
			def __init__(self, allocator=None, *args, **kwargs):
				super().__init__(None) # Triggers _obj.setter through object.__setattr__
				object.__setattr__(self, "_allocator", allocator)
				object.__setattr__(self, "_args", args)
				object.__setattr__(self, "_kwargs", kwargs)
				object.__setattr__(self, "_test", -1)

			@property
			def test(self):
				return self._test
			
			@test.setter
			def test(self, value):
				object.__setattr__(self, "_test", value)


			@property
			def _obj(self):
				if self._wobj is None:
					wobj = self._allocator(*self._args, **self._kwargs)
					object.__setattr__(self, "_wobj", wobj)
				return self._wobj

			@_obj.setter
			def _obj(self, value):
				object.__setattr__(self, "_wobj", value)

		class W(WeaklyAllocated):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)

			@property
			def _obj(self):
				obj = getattr(self._wobj, "inst", None)
				if obj is None:
					obj = self._allocator(*self._args, **self._kwargs)
					self._wobj.inst = obj
				return obj

			@_obj.setter
			def _obj(self, value):
				tloc = self.__dict__.get("_wobj")
				if tloc is None:
					tloc = threading.local()
					object.__setattr__(self, "_wobj", tloc)
				tloc.inst = value

			@property
			def test(self):
				return self._test
			
			@test.setter
			def test(self, value):
				self._test = value

		w = W(A, 1, 2)
		assert w.a == 1
		assert w.test == -1
		w.test = 10
		assert w.test == 10

	# test1()
	test2()



def test():
	log(title("Property Test"))
	property_test()
	log(title("End of Property Test"))

run()
