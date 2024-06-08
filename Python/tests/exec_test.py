from test import *


class A:
	def f(self):
		log("A.f()")

def test():
	exec("""def ff():
	log("ff()")
	a = A()
	a.f()
ff()""")
run()