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
		assert self.on_call.is_subscribed(self.cb_id)
		self.cb_id2 = self.on_call.subscribe(self._on_call)
		assert self.on_call.is_subscribed(self.cb_id2)

	def subscribe_subscription(self):
		sub = Subscription()
		self.cb_id = self.on_call.subscribe(sub)
		self.on_call()
		assert self.on_call.is_subscribed(self.cb_id)
		self.on_call.unsubscribe(self.cb_id)
		assert not self.on_call.is_subscribed(self.cb_id)

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
	assert_exception("a.subscribe_independent_no_subscriber()", False)
	assert_exception("assert a.on_call.unsubscribe(a.cb_id) == False", False)
	log(title("End of test_independent_cb_no_subscriber()"))

def test_independent_cb_with_subscriber():
	log(title("test_independent_cb_with_subscriber()"))
	log.expr("a = A()")
	assert_exception("a.subscribe_independent_with_self()", False)
	assert_exception("assert a.on_call.is_subscribed(a.cb_id)", False)
	assert_exception("assert a.on_call.is_subscribed(a.cb_id2)", False)
	log.expr("a()")
	log.expr("b = B()")
	assert_exception("b.subscribe_independent_with_self(a)", False)
	assert_exception("assert a.on_call.is_subscribed(b.cb_id)", False)
	assert_exception("assert a.on_call.is_subscribed(b.cb_id2)", False)
	log.expr("a()")
	log(title("End of test_independent_cb_with_subscriber()"))

def test_dependent_cb():
	log(title("test_dependent_cb()"))
	log.expr("a = A()")
	assert_exception("a.subscribe_dependent()", False)
	assert_exception("assert a.on_call.is_subscribed(a.cb_id)", False)
	log.expr("a()")
	log.expr("b = B()")
	assert_exception("b.subscribe_dependent(a)", False)
	assert_exception("assert a.on_call.is_subscribed(b.cb_id)", False)
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


def test_subscribe_subscription():
	log(title("test_subscribe_subscription()"))
	log.expr("a = A()")
	log.expr("a.subscribe_subscription()")
	assert_exception("assert a.on_call.is_subscribed(a.cb_id) is False", False)
	log(title("End of test_subscribe_subscription()"))

def test():
	log(title("Subscription Test"))
	test_independent_cb_no_subscriber()
	test_independent_cb_with_subscriber()
	test_dependent_cb()
	test_dependent_cb_destroy()
	test_subscribe_subscription()
	log(title("Subscription Test finished"))

run()
