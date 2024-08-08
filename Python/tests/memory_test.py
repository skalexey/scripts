from test import *

from utils.concurrency.thread_local_proxy import ThreadLocalProxy
from utils.memory.lazy_allocated import LazyAllocated
from utils.proxy import Proxy


def memory_test():
	class A:
		def __init__(self, a=None, b=None):
			log(utils.method.msg_kw())
			self.a = a
			self.b = b
			self.f_called = False

		def f(self):
			log(utils.method.msg_kw(f"a={self.a}, b={self.b}"))
			self.f_called = True

	def proxy_test():
		log(title("Proxy Test"))

		a = A()
		proxy = Proxy(a)
		proxy.f()
		assert a.f_called
		log(title("End of Proxy Test"))

	def lazy_allocated_test():
		log(title("LazyAllocated Test"))
		wa = LazyAllocated(A, 1, 2)
		log(utils.method.msg_kw("LazyAllocated object created"))
		wa.f()
		assert wa._obj.f_called
		assert wa._obj.a == 1
		assert wa._obj.b == 2
		wa.a = 3
		assert wa._obj.a == 3
		assert wa.a == 3

		wa = LazyAllocated(A, a=2, b=3)
		assert wa._obj.a == 2
		assert wa._obj.b == 3
		log(title("End of LazyAllocated Test"))

	def thread_local_proxy_test():
		log(title("ThreadLocalProxy Test"))
		tl = ThreadLocalProxy(A, 1, 2)
		log(utils.method.msg_kw("ThreadLocalProxy object created"))
		tl.f()
		assert tl.f_called
		assert tl.a == 1
		assert tl._obj.b == 2
		tl.a = 3
		assert tl.a == 3
		assert tl._obj.a == 3

		tl = ThreadLocalProxy(A, a=2, b=3)
		assert tl.a == 2
		assert tl._obj.b == 3
		tl.a = 4
		tl._obj.b = 5
		assert tl.b == 5
		assert tl._obj.b == 5
		assert not tl.f_called

		def job():
			tl.f()
			assert tl.f_called
			assert tl._obj.a == 2
			assert tl.b == 3
			tl.a = 6
			tl._obj.b = 7
			assert tl._obj.a == 6
			assert tl.b == 7

		thread = threading.Thread(target=job)
		thread.start()
		thread.join()
		assert not tl.f_called
		assert tl.a == 4
		assert tl._obj.b == 5

		log(title("End of ThreadLocalProxy Test"))

	# proxy_test()
	# lazy_allocated_test()
	thread_local_proxy_test()

def test():
	log(title("Memory Test"))
	memory_test()
	log(title("End of Memory Test"))

run()
