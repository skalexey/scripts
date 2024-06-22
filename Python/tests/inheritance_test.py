from test import *


def init_test():
	log(title("Init Test"))
	class A:
		def __init__(self):
			log("A.__init__()")
			super().__init__()

	class B(A):
		def __init__(self):
			log("B.__init__()")
			super().__init__()

	class C:
		def __init__(self):
			log("C.__init__()")

	class D(A, C):
		def __init__(self):
			log("D.__init__()")
			super().__init__()

	class E:
		def __init__(self):
			log("E.__init__()")

	class F(A, E):
		def __init__(self):
			log("F.__init__()")
			A.__init__(self)
			E.__init__(self)
			super().__init__()
	log.expr("d = D()")
	log.expr("b = B()")
	log.expr("a = A()")
	log.expr("f = F()")
	log(title("End of Init Test"))
	

def test():
	log(title("Inheritance Test"))
	init_test()
	log(title("End of Inheritance Test"))

run()