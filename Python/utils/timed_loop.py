from contextlib import contextmanager
from time import time

from utils.debug.debug_detector import debug_timespan


class Controller:
	def __init__(self, timeout):
		self.timeout = timeout
		self.last_time = time()
		self.elapsed_time = 0
		self.attempt = 0
		self.timedout = False

	def iterate(self):
		self.attempt += 1
		return self.update()

	def update(self):
		current_time = time()
		dt = current_time - self.last_time
		self.elapsed_time += dt
		if self.attempt > 1:
			_debug_timespan = debug_timespan(self)
			self.elapsed_time -= min(self.elapsed_time, _debug_timespan)
		assert self.elapsed_time >= 0, f"Elapsed time is negative: {self.elapsed_time}"
		if self.elapsed_time >= self.timeout:
			self.timedout = True
		self.last_time = current_time
		return not self.timedout
	
	def __repr__(self):
		return f"{self.__class__.__name__}(attempt={self.attempt}, elapsed_time={self.elapsed_time}, timedout={self.timedout})"

def timed_loop(timeout):
	controller = Controller(timeout)
	while controller.iterate():
		yield controller  # Yield control back to the user’s block
	yield controller

def timedout(timeout):
	controller = Controller()
	while controller.iterate(timeout):
		yield controller.timedout  # Yield control back to the user’s block
	yield controller.timedout


if __name__ == "__main__":
	try:
		for loop in timed_loop(10):
			print("Doing something...")
			if loop.attempt == 3:
				print(f"Breaking the loop on {loop.attempt}...")
				break

		for loop in timed_loop(1):
			print("Doing something...")

		for tm in timedout(1):
			print(f"Doing something while timedout is {tm}...")
			# User-defined logic here
			# Simulate a condition to break the loop if needed
			# some_condition = True  # Change this condition as needed
			# if some_condition:
			#     controller.stop()

		# with timed_loop(1):
		# 	print("Doing something AGAIN!!!...")
			# Additional user-defined logic here

	except TimeoutError as e:
		print(e)
