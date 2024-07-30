from test import *


def arg_test():
	def f(*args, x=None, y=None, data=None):
		log(f"x: {x}, y: {y}, data: {data}, args: {args}")
	f(1, 2, 3, 4, x=5, y=6)

def scope_test():
	for i in range(3):
		a = "gee"
	log(f"a: {a}")
	
def event_test():
	log(title("Event Test"))
	import threading
	event = threading.Event()
	assert event.is_set() == False
	event.set()
	assert event.is_set() == True
	event.set()
	event.set()
	event.set()
	assert event.is_set() == True
	event.wait()
	event.clear()
	assert event.is_set() == False
	log(title("End of Event Test"))

def compare_exceptions_test():
	e1 = TypeError("Test")
	e2 = TypeError("Test")
	assert e1 != e2
	assert e1.args == e2.args
	assert type(e1) == type(e2)

	e3 = TypeError("Test 2")
	assert e1 != e3
	assert e1.args != e3.args

	e4 = ValueError("Test")
	assert e1 != e4
	assert e1.args == e4.args

def for_range_test():
	for i in range(0):
		assert False, "Should not enter the loop"

	for i in range(1):
		log(i)

def for_enumerate_test():
	for i, v in enumerate([1, 2, 3], start=2):
		log(f"i: {i}, v: {v}")

def test():
	log(title("Quick Test"))

	for_enumerate_test()
	
	log(title("End of Quick Test"))

run()