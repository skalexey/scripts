import gc
from test import *

from utils.subscription import *


class A:
	def __init__(self):
		super().__init__()
		self.on_call = Subscription()

	def subscribe_independent_no_subscriber(self):
		def on_call():
			log("A.on_call()")
		self.cb_id = self.on_call.subscribe(on_call)
		def on_call2():
			log("A.on_call2()")
		self.cb_id2 = self.on_call.subscribe(on_call2)

	def subscribe_independent_with_self(self):
		def on_call():
			log("A.on_call()")
		self.cb_id = self.on_call.subscribe(on_call, self)
		def on_call2():
			log("A.on_call2()")
		self.cb_id2 = self.on_call.subscribe(on_call2, self)

	def subscribe_dependent(self):
		self.cb_id = self.on_call.subscribe(self._on_call)
		assert(self.on_call.is_subscribed(self.cb_id))
		self.cb_id2 = self.on_call.subscribe(self._on_call)
		assert(self.on_call.is_subscribed(self.cb_id2))

	def _on_call(self):
		log("A._on_call()")

	def __call__(self):
		log("A.__call__()")
		self.on_call()

	def __del__(self):
		log("A.__del__()")

class B:
	def __init__(self):
		super().__init__()

	def subscribe_independent_with_self(self, a: A):
		def on_call():
			log("B.on_call()")
		self.cb_id = a.on_call.subscribe(on_call, self)
		def on_call2():
			log("B.on_call2()")
		self.cb_id2 = a.on_call.subscribe(on_call2, self)

	def subscribe_dependent(self, a: A):
		self.cb_id = a.on_call.subscribe(self._on_a_call)

	def _on_a_call(self):
		log("B._on_a_call()")

	def __del__(self):
		log("B.__del__()")

def test_independent_cb_no_subscriber():
	log(title("test_independent_cb_no_subscriber()"))
	log.expr("a = A()")
	log.expr("a.subscribe_independent_no_subscriber()")
	log.expr("assert(a.on_call.unsubscribe(a.cb_id) == False)")
	log(title("End of test_independent_cb_no_subscriber()"))

def test_independent_cb_with_subscriber():
	log(title("test_independent_cb_with_subscriber()"))
	log.expr("a = A()")
	log.expr("a.subscribe_independent_with_self()")
	log.expr("assert(a.on_call.is_subscribed(a.cb_id))")
	log.expr("assert(a.on_call.is_subscribed(a.cb_id2))")
	log.expr("a()")
	log.expr("b = B()")
	log.expr("b.subscribe_independent_with_self(a)")
	log.expr("assert(a.on_call.is_subscribed(b.cb_id))")
	log.expr("assert(a.on_call.is_subscribed(b.cb_id2))")
	log.expr("a()")
	log(title("End of test_independent_cb_with_subscriber()"))

def test_dependent_cb():
	log(title("test_dependent_cb()"))
	log.expr("a = A()")
	log.expr("a.subscribe_dependent()")
	log.expr("assert(a.on_call.is_subscribed(a.cb_id))")
	log.expr("a()")
	log.expr("b = B()")
	log.expr("b.subscribe_dependent(a)")
	log.expr("assert(a.on_call.is_subscribed(b.cb_id))")
	log.expr("a()")
	log(title("End of test_dependent_cb()"))

def test_dependent_cb_destroy():
	log(title("test_dependent_cb()"))
	log.expr("a = A()")
	log.expr("a.subscribe_dependent()")
	log.expr("""
def subscribe_b(a):
	b = B()
	b.subscribe_dependent(a)
	a()
subscribe_b(a)"""
	)
	log.expr("a()")
	log(title("End of test_dependent_cb()"))

def test():
	log(title("Subscription Test"))
	test_independent_cb_no_subscriber()
	test_independent_cb_with_subscriber()
	test_dependent_cb()
	test_dependent_cb_destroy()
	log(title("Subscription Test finished"))

run()
