from utils.log import *

logger = Logger("inetanceof_test")

class A:
	pass

class B(A):
	pass

class C(B):
	pass

class D:
	pass

if __name__ == "__main__":
	logger.log_expr_and_val("issubclass(C, A)", globals(), locals())
	logger.log_expr_and_val("issubclass(C, B)", globals(), locals())
	logger.log_expr_and_val("issubclass(C, C)", globals(), locals())
	logger.log_expr_and_val("issubclass(C, object)", globals(), locals())
	logger.log_expr_and_val("issubclass(D, A)", globals(), locals())

	# isinstance test
	# logger.log_expr("c=C()", globals(), locals())
	c = C()
	logger.log_expr_and_val("isinstance(c, A)", globals(), locals())
	logger.log_expr_and_val("isinstance(c, B)", globals(), locals())
	logger.log_expr_and_val("isinstance(c, C)", globals(), locals())
	logger.log_expr_and_val("isinstance(c, object)", globals(), locals())
	logger.log_expr_and_val("isinstance(c, D)", globals(), locals())

	logger.log_expr_and_val("isinstance(None, A)", globals(), locals())
