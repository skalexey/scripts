import traceback

import utils.thread
from utils.log.logger import Logger

log = Logger()

def raise_async(exception):
	try:
		raise exception
	except Exception as e:
		exc_type, exc_value, exc_traceback = sys.exc_info()

	def raise_job(exc_type, exc_value, exc_traceback):
		# Print the callstack:
		ex_info = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
		log(f"Raising exception: {ex_info}")
		raise exc_type(exc_value).with_traceback(exc_traceback)

	return utils.thread.do_async(raise_job, exc_type, exc_value, exc_traceback)

class EnsureCall:
	class State:
		def __init__(self, func):
			self.func = func
			self.called = False
			self.exception_raised = None

		def call(self, *args, **kwargs):
			self.func(*args, **kwargs)
			self.called = True

	def __init__(self, func):
		self.state = self.State(func)

	def __call__(self, *args, **kwargs):
		self.state.call(*args, **kwargs)

	def __del__(self):
		if not self.state.called:
			# Throw in a separate thread and wait for the result
			ex = Exception("Function was not called before the object was destroyed.")
			raise_async(ex).result()
			self.state.exception_raised = ex


if __name__ == "__main__":
	from tests.test import *

	# Usage example
	def my_function():
		print("Function called")
	
	ec = EnsureCall(my_function)
	state = ec.state
	del ec
	assert state.exception_raised is not None, "Expected exception"
	log("Test 1 passed")
	ec = EnsureCall(my_function)
	state = ec.state
	ec()
	del ec
	assert state.exception_raised is None, "Unexpected exception"
	log("Test 2 passed")
	print("All tests passed")
