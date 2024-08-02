import re
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

def re_test():
	def f(msg):
		# Find only first occurance that is alwais in the beginning of the line
		regex = r"^\[([^\]]+)\]"
		# Print all found occurances:
		for match in re.finditer(regex, msg):
		 	log(f"match: {match.group(1)}")
		# Print the first found occurance:
		result = re.search(regex, msg)
		if result:
			result = result.group(1)
			log(f"result: {result}")

	f("Hello [world]")
	f("Hello [world] [world2]")
	f("Hello [world] [world2] [world3]")
	f("[fsdifj] Hello [world] [world2] [world3]")

def timestamp_test():
	log(f"Timestamp: {time()}")

def none_access_error_test():
	def catch_test():
		try:
			a = None
			a.x()
		except AttributeError as e:
			log(f"Caught AttributeError: {e}")
			return
		assert False, "Did not catch AttributeError"
	catch_test()

def lock_with_test():
	import threading

	# Using Lock with the with statement
	lock = threading.Lock()

	with lock as acquired_lock:
		print("Lock acquired:", acquired_lock is lock)  # Output: Lock acquired: True

	# Using RLock with the with statement
	rlock = threading.RLock()

	with rlock as acquired_rlock:
		print("RLock acquired:", acquired_rlock is rlock)  # Output: RLock acquired: True


def test():
	log(title("Quick Test"))

	lock_with_test()
	
	log(title("End of Quick Test"))


run()