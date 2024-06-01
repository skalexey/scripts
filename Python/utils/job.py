from utils.subscription import *
from utils.math.utility import *

class Job:
	def __init__(self, *args, **kwargs):
		self.on_done = Subscription()
		self.on_cancel = Subscription()

	def update(self, dt):
		return False

	def is_done(self):
		return False

	def cancel(self):
		self.on_cancel.notify()

class TimedJob(Job):
	def __init__(self, duration = None, duration_range = None):
		super().__init__()
		self.time_elapsed = 0
		if duration is not None:
			self.duration = duration
		else:
			range = duration_range if duration_range is not None else Range(0.4, 3.6)
			self.duration = range.random()

	def is_done(self):
		return self.time_elapsed >= self.duration

	def update(self, dt):
		self.time_elapsed += dt
		if self.is_done():
			self.on_done.notify()
			return True
		return False
