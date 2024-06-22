from test import *

import utils.inspect_utils as inspect_utils


def call_info_test():
	log(title("Call Info Test"))
	class A:
		def instance_method(self):
			call_info = inspect_utils.call_info()
			log(f"Instance method call info: {call_info}")
		@classmethod
		def class_method(cls):
			call_info = inspect_utils.call_info()
			log(f"Instance method call info: {call_info}")

	class B(A):
		def instance_method(self):
			super().instance_method()

		@classmethod
		def class_method(cls):
			call_info = inspect_utils.call_info()
			log(f"Instance method call info: {call_info}")

	class C(B):
		pass

	# Calling methods to test
	c = C()
	c.instance_method()
	C.class_method()  
	B.class_method()
	A.class_method()
	log(title("End of Call Info Test"))

def test():
	call_info_test()

run()