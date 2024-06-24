from test import *


def arg_test():
	def f(*args, x=None, y=None, data=None):
		log(f"x: {x}, y: {y}, data: {data}, args: {args}")
	f(1, 2, 3, 4, x=5, y=6)

def scope_test():
	for i in range(3):
		a = "gee"
	log(f"a: {a}")

def test():
	log(title("Quick Test"))

	scope_test()
	
	log(title("End of Quick Test"))

run()