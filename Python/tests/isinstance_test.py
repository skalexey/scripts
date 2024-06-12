from utils.log.logger import *

log = Logger()

class A:
	pass

class B(A):
	pass

class C(B):
	pass

class D:
	pass

if __name__ == "__main__":
	log.expr_and_val("issubclass(C, A)", globals(), locals())
	log.expr_and_val("issubclass(C, B)", globals(), locals())
	log.expr_and_val("issubclass(C, C)", globals(), locals())
	log.expr_and_val("issubclass(C, object)", globals(), locals())
	log.expr_and_val("issubclass(D, A)", globals(), locals())

	# isinstance test
	# log.expr("c=C()", globals(), locals())
	c = C()
	log.expr_and_val("isinstance(c, A)", globals(), locals())
	log.expr_and_val("isinstance(c, B)", globals(), locals())
	log.expr_and_val("isinstance(c, C)", globals(), locals())
	log.expr_and_val("isinstance(c, object)", globals(), locals())
	log.expr_and_val("isinstance(c, D)", globals(), locals())

	log.expr_and_val("isinstance(None, A)", globals(), locals())
