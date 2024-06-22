from test import *


def kwargs_test():
	log(title("Kwargs Test"))
	def f2(*args, **kwargs):
		log(f"f2({args}, {kwargs})")
		log(f"type of args: {type(args)}")
		log(f"type of kwargs: {type(kwargs)}")

	def f(a, b, c=None):
		f2(a, b, c)
	f(1, 2, 3)
	log(title("End of Kwargs Test"))

def test():
	log(title("Args Test"))
	kwargs_test()
	log(title("End of Args Test"))

run()