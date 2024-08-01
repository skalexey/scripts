import threading
from test import *


def lock_test():
	log(title("Lock Test"))
	lock = threading.RLock()
	log(f"lock: {lock!r}")
	lock.acquire()
	log(f"lock: {lock!r}")
	log(title("End of Lock Test"))

def test():
	log(title("Lock Test"))
	lock_test()
	log(title("End of Lock Test"))

run()
