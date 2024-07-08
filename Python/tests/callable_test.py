from test import *

import utils.function
import utils.method
from utils.memory import Callable, OwnedCallable, SmartCallable


def init_test():
	log(title("Callable Test"))

	class A:
		def s(self):
			log(utils.method.msg())

	def f():
		log(utils.function.msg())

	a = A()

	sc = SmartCallable(f, a)
	assert hasattr(a, "__smartcbs__")
	sc()
	del sc
	assert not hasattr(a, "__smartcbs__")

	class CallableInfo(OwnedCallable):
		def __init__(self, *args, unsubscribe_on_false=None, priority=None, **kwargs):
			super().__init__(*args, invalidate_on_false=unsubscribe_on_false, **kwargs)
			self.priority = priority or 0
		
	class CallableInfoCleanOnDestroy(CallableInfo, SmartCallable):
		pass

	def closed_scope():
		log(title("Closed Scope"))
		ci = CallableInfoCleanOnDestroy(f, a)
		assert hasattr(a, "__smartcbs__")
		ci()
		log(title("End of Closed Scope"))
	
	closed_scope()
	assert not hasattr(a, "__smartcbs__")
	log(title("End of Callable Test"))


def callable_test():
	init_test()

def test():
	log(title("Callable Test"))
	callable_test()
	log(title("End of Callable Test"))

run()
