import threading
from datetime import datetime

from utils.context import GlobalContext
from utils.subscription import Subscription


class DebugDetector:
	def __init__(self):
		self.debug_detection_threshold = 1.0
		self.last_debug_timespan = 0
		self.debug_detection_lock = threading.Lock()
		self.on_debug_detected = Subscription()
		self.on_debug_detected.subscribe(self._on_debug_detected)
		self._last_check_time = None
		self._last_debug_timespan_checkin = set()
		self._thread = threading.Thread(target=self._debug_detection_job)

	def _on_debug_detected(self):
		self._last_debug_timespan_checkin.clear()

	def check_debug_detection(self):
		with self.debug_detection_lock:
			current_time = datetime.now().timestamp()
			dt = current_time - (self._last_check_time or current_time)
			if dt > self.debug_detection_threshold:
				self.last_debug_timespan = dt
				self.on_debug_detected()
			self._last_check_time = current_time

	def grab_last_debug_timespan(self, checker):
		self.check_debug_detection()
		checkin = checker in self._last_debug_timespan_checkin
		if checkin:
			return 0
		self._last_debug_timespan_checkin.add(checker)
		return self.last_debug_timespan

	def _debug_detection_job(self):
		while True:
			self.check_debug_detection()
			threading.thread.sleep(0.1)
