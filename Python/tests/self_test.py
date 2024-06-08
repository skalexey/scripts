from test import *


class A:
	def f(self):
		log("A.f()")

	def g(self):
		log("A.g()")
		def e(self):
			log("g.e()")
			f()
		e(self)

def test():
	log(title("Self Test"))
	a = A()
	a.g()
	log(title("End of Self Test"))

run()
