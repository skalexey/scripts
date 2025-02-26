from test import *
import sys

class StderrOverride:
	def __init__(self):
		self._stderr = sys.stderr
		sys.stderr = self
	def write(self, s):
		self._stderr.write(s)
		log(s)
	def flush(self):
		self._stderr.flush()
	def __del__(self):
		sys.stderr = self._stderr
		self._stderr = None

def exception_print_test():
	sys.stderr = StderrOverride()
	raise Exception("Test exception")

def test():
	log(title("Exception Print Test"))
	exception_print_test()
	log(title("End of Exception Print Test"))

run()
