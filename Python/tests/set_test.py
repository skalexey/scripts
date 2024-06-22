from test import *


def intersection_test():
	log(title("Intersection Test"))
	log.expr("a = set([1, 2, 3])")
	log.expr("b = set([2, 3, 4])")
	log.expr("c = a & b")
	log.expr_and_val("c")
	log(title("End of Intersection Test"))

def union_test():
	log(title("Union Test"))
	log.expr("a = set([1, 2, 3])")
	log.expr("b = set([2, 3, 4])")
	log.expr("c = a | b")
	log.expr_and_val("c")
	log(title("End of Union Test"))

def difference_test():
	log(title("Difference Test"))
	log.expr("a = set([1, 2, 3])")
	log.expr("b = set([2, 3, 4])")
	log.expr("c = a - b")
	log.expr_and_val("c")
	log.expr_and_val("set([1, 2, 3]) - set([1, 3, 2, 4, 5, 6])")
	log(title("End of Difference Test"))

def symmetric_difference_test():
	log(title("Symmetric Difference Test"))
	log.expr("a = set([1, 2, 3])")
	log.expr("b = set([2, 3, 4])")
	log.expr("c = a ^ b")
	log.expr_and_val("c")
	log(title("End of Symmetric Difference Test"))

def issubset_test():
	log(title("Is Subset Test"))
	log.expr("a = set([1, 2, 3])")
	log.expr("b = set([2, 3])")
	log.expr("c = a <= b")
	log.expr_and_val("c")
	log(title("End of Is Subset Test"))

def issuperset_test():
	log(title("Is Superset Test"))
	log.expr("a = set([1, 2, 3])")
	log.expr("b = set([2, 3])")
	log.expr("c = a >= b")
	log.expr_and_val("c")
	log(title("End of Is Superset Test"))

def test():
	log(title("Set Test"))
	intersection_test()
	union_test()
	difference_test()
	symmetric_difference_test()
	issubset_test()
	issuperset_test()
	log(title("End of Set Test"))

run()
