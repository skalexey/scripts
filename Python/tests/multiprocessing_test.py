import multiprocessing
from test import *


class A:
	def __init__(self, x):
		self.x = x

def multiprocessing_test2(recursion_level):
	log(title(f"Multiprocessing Test 2 with {recursion_level} recursion levels"))
	d = multiprocessing.Manager().dict()
	a = A(None)
	t = a
	for i in range(recursion_level):
		n = A(t)
		t.x = n
		t = n
	d['ref'] = a
	log(title("End of Multiprocessing Test 2"))

def multiprocessing_test():
	log(title("Multiprocessing Test"))
	# Code
	log(title("End of Multiprocessing Test"))
	p = multiprocessing.Process(target=multiprocessing_test2)
	p.start()
	p.join()

def test():
	multiprocessing_test2(1)
	multiprocessing_test2(100)
	current_recursion_limit = sys.getrecursionlimit()
	log.info(f"Current recursion limit: {current_recursion_limit}")
	with AssertExceptionType(RecursionError):
		multiprocessing_test2(350)
	sys.setrecursionlimit(current_recursion_limit * 2)
	multiprocessing_test2(350)
	

if __name__ == "__main__":
	run()
