from test import *


def length_test():
	log(title("List Length Test"))
	elements = [1, 2, 3, 4, 5]
	log(elements)
	log("Length of elements: " + str(len(elements)))
	log(title("End of List Length Test"))

def empty_list_test():
	log(title("Empty List Test"))
	elements = []
	log(elements or 'Empty')
	log(title("End of Empty List Test"))

def test():
	log(title("List Test"))
	length_test()
	empty_list_test()
	log(title("End of List Test"))

run()