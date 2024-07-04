from test import *

from utils.collection.ordered_dict import OrderedDict


def instantiate_test():
	d = {12: "a", 22: "b", 32: "c"}
	od = OrderedDict(d)
	assert od == d
	log(od)

def ordered_dict_test():
	instantiate_test()

def test():
	log(title("Ordered Dict Test"))
	ordered_dict_test()
	log(title("End of Ordered Dict Test"))

run()
