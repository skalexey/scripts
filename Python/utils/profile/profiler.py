import time


class TimeProfiler:
	def __init__(self):
		self.start_time = None
		self.last_time = None
		self._print_function = print
		super().__init__()
	
	def start(self):
		self.start_time = time.time()
		self.last_time = self.start_time

	def mark(self):
		self.last_time = time.time()
		if self.start_time is None:
			self.start_time = self.last_time

	def measure(self):
		return time.time() - self.start_time

	def print_measure(self):
		measured_time = self.measure()
		self.print(f"Time elapsed: {measured_time}")

	def print(self, message):
		self._print_function(message)

	def set_print_function(self, print_function):
		self._print_function = print_function
