import gc
from test import *

from utils.subscription import *


class A:
	def __init__(self):
		super().__init__()
		self.on_call = Subscription()

	def subscribe_independent_no_subscriber(self):
		def on_call():
			logger.log("A.on_call()")
		self.cb_id = self.on_call.subscribe(on_call)
		def on_call2():
			logger.log("A.on_call2()")
		self.cb_id2 = self.on_call.subscribe(on_call2)

	def subscribe_independent_with_self(self):
		def on_call():
			logger.log("A.on_call()")
		self.cb_id = self.on_call.subscribe(on_call, self)
		def on_call2():
			logger.log("A.on_call2()")
		self.cb_id2 = self.on_call.subscribe(on_call2, self)

	def subscribe_dependent(self):
		self.cb_id = self.on_call.subscribe(self._on_call)
		assert(self.on_call.is_subscribed(self.cb_id))
		self.cb_id2 = self.on_call.subscribe(self._on_call)
		assert(self.on_call.is_subscribed(self.cb_id2))

	def _on_call(self):
		logger.log("A._on_call()")

	def __call__(self):
		logger.log("A.__call__()")
		self.on_call()

	def __del__(self):
		logger.log("A.__del__()")

class B:
	def __init__(self):
		super().__init__()

	def subscribe_independent_with_self(self, a: A):
		def on_call():
			logger.log("B.on_call()")
		self.cb_id = a.on_call.subscribe(on_call, self)
		def on_call2():
			logger.log("B.on_call2()")
		self.cb_id2 = a.on_call.subscribe(on_call2, self)

	def subscribe_dependent(self, a: A):
		self.cb_id = a.on_call.subscribe(self._on_a_call)

	def _on_a_call(self):
		logger.log("B._on_a_call()")

	def __del__(self):
		logger.log("B.__del__()")

def test_independent_cb_no_subscriber():
	logger.log(title("test_independent_cb_no_subscriber()"))
	logger.log_expr("a = A()")
	logger.log_expr("a.subscribe_independent_no_subscriber()")
	logger.log_expr("assert(a.on_call.unsubscribe(a.cb_id) == False)")
	logger.log(title("End of test_independent_cb_no_subscriber()"))

def test_independent_cb_with_subscriber():
	logger.log(title("test_independent_cb_with_subscriber()"))
	logger.log_expr("a = A()")
	logger.log_expr("a.subscribe_independent_with_self()")
	logger.log_expr("assert(a.on_call.is_subscribed(a.cb_id))")
	logger.log_expr("assert(a.on_call.is_subscribed(a.cb_id2))")
	logger.log_expr("a()")
	logger.log_expr("b = B()")
	logger.log_expr("b.subscribe_independent_with_self(a)")
	logger.log_expr("assert(a.on_call.is_subscribed(b.cb_id))")
	logger.log_expr("assert(a.on_call.is_subscribed(b.cb_id2))")
	logger.log_expr("a()")
	logger.log(title("End of test_independent_cb_with_subscriber()"))

def test_dependent_cb():
	logger.log(title("test_dependent_cb()"))
	logger.log_expr("a = A()")
	logger.log_expr("a.subscribe_dependent()")
	logger.log_expr("assert(a.on_call.is_subscribed(a.cb_id))")
	logger.log_expr("a()")
	logger.log_expr("b = B()")
	logger.log_expr("b.subscribe_dependent(a)")
	logger.log_expr("assert(a.on_call.is_subscribed(b.cb_id))")
	logger.log_expr("a()")
	logger.log(title("End of test_dependent_cb()"))

def test_dependent_cb_destroy():
	logger.log(title("test_dependent_cb()"))
	logger.log_expr("a = A()")
	logger.log_expr("a.subscribe_dependent()")
	logger.log_expr("""
def subscribe_b(a):
	b = B()
	b.subscribe_dependent(a)
	a()
subscribe_b(a)"""
	)
	logger.log_expr("a()")
	logger.log(title("End of test_dependent_cb()"))

def test():
	logger.log(title("Subscription Test"))
	test_independent_cb_no_subscriber()
	test_independent_cb_with_subscriber()
	test_dependent_cb()
	test_dependent_cb_destroy()
	logger.log(title("Subscription Test finished"))

run()
