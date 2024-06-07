from test import *


class A:
	def f(self):
		logger.log("A.f()")

	def g(self):
		logger.log("A.g()")
		def e(self):
			logger.log("g.e()")
			f()
		e(self)

def test():
	logger.log(title("Self Test"))
	a = A()
	a.g()
	logger.log(title("End of Self Test"))

run()
