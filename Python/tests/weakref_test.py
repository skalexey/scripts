import gc
import weakref
from test import *


def WeakValueDictionary_test():
	log(title("WeakValueDictionary Test"))
	d = dict(a=1, b=2)
	with AssertExceptionType():
		ref = weakref.ref(d)
	wd = weakref.WeakValueDictionary()
	wd.d = d
	d["a"] = 3
	log(f"d: {d}")
	assert wd.d["a"] == 3
	log(f"wd.d: {wd.d}")
	del d
	gc.collect()
	log(f"wd.d 2: {wd.d}")
	log(title("End of WeakValueDictionary Test"))

def weakref_test():
	WeakValueDictionary_test()

def test():
	log(title("Weakref Test"))
	weakref_test()
	log(title("End of Weakref Test"))

run()
