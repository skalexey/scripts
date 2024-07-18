from utils.math.range import Range
from utils.profile.trackable_resource import TrackableResource
from utils.subscription import Subscription


class Job(TrackableResource):
	def __init__(self, *args, **kwargs):
		self.on_done = Subscription()
		self.on_cancel = Subscription()
		self._cancelled = False
		super().__init__(*args, **kwargs)

	def update(self, dt):
		if self.is_done():
			if self.is_cancelled():
				self.on_cancel.notify(self)
			else:
				self.on_done.notify(self)
			return True
		return False

	def is_done(self):
		return self.is_cancelled() # Default

	def is_cancelled(self):
		return self._cancelled

	def cancel(self):
		self._cancelled = True
		self.on_cancel.notify(self)

class TimedJob(Job):
	def __init__(self, duration = None, duration_range=None, *args, **kwargs):
		self.time_elapsed = 0
		if duration is not None:
			self.duration = duration
		else:
			range = duration_range if duration_range is not None else Range(0.4, 3.6)
			self.duration = range.random()
		super().__init__(*args, **kwargs)

	def is_done(self):
		if super().is_done():
			return True
		return self.time_elapsed >= self.duration

	def update(self, dt):
		self.time_elapsed += dt
		return super().update(dt)
