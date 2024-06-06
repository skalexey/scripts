from test import *


class A:
	def f(self):
		logger.log("A.f()")

def test():
	exec("""def ff():
	logger.log("ff()")
	a = A()
	a.f()
ff()""")
run()