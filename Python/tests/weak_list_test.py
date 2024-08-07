from test import *

from utils.collection.weak_list import WeakList
from utils.memory import WeakProxy


def weak_list_test():
	def number_test():
		log(title("Number Test"))
		lst = [1, 2, 3]
		wlst = WeakList(lst)
		assert lst == wlst
		wlst.remove(2)
		assert lst != wlst
		log(title("End of Number Test"))

	class A:
			def __init__(self, value=None):
				self.value = value

	def object_test():
		log(title("Object Test"))

		a = A(1)
		b = A(2)
		lst = [a, b, A(3)]
		wp = WeakProxy(a)
		assert wp == a
		wp = WeakProxy(lst[0])
		assert wp == lst[0]
		lst2 = list(lst)
		assert lst == lst2
		wlst = WeakList(lst)
		assert lst == wlst
		del lst[1]
		assert lst != wlst
		lst.insert(1, b)
		assert lst == wlst
		del a # Still stored in lst
		assert lst == wlst
		log(title("End of Object Test"))

	def getitem_test():
		log(title("Get Item Test"))
		lst = [A(i) for i in range(3)]
		wlst = WeakList(lst)
		for item in wlst:
			assert isinstance(item, A)
		log(title("End of Get Item Test"))

	number_test()
	object_test()
	getitem_test()

def test():
	log(title("Weak List Test"))
	weak_list_test()
	log(title("End of Weak List Test"))

run()
