import threading
from datetime import datetime
from time import sleep

import utils  # Lazy import for less important modules
from utils.debug import wrap_debug_lock


class DebugDetector:
	def __init__(self):
		self.debug_detection_threshold = 1.0
		self.last_debug_timespan = 0
		self.debug_detection_lock = wrap_debug_lock(threading.Lock())
		self._on_debug_detected_subscription = None # Created on demand through on_debug_detected property 
		self._last_check_time = None
		self._last_debug_timespan_checkin = set()
		self._thread = threading.Thread(target=self._debug_detection_job, name="DebugDetector")
		self._thread.start()

	@property
	def on_debug_detected(self):
		result = self._on_debug_detected_subscription
		if result is None:
			result = utils.subscription.Subscription()
			self._on_debug_detected_subscription = result
			self.on_debug_detected.subscribe(self._on_debug_detected)
		return result

	def _on_debug_detected(self):
		self._last_debug_timespan_checkin.clear()

	def check_debug_detection(self):
		with self.debug_detection_lock:
			current_time = datetime.now().timestamp()
			dt = current_time - (self._last_check_time or current_time)
			self._last_check_time = current_time
			if dt > self.debug_detection_threshold:
				self.last_debug_timespan = dt
				self.on_debug_detected.notify()

	def grab_last_debug_timespan(self, checker):
		self.check_debug_detection()
		checkin = checker in self._last_debug_timespan_checkin
		if checkin:
			return 0
		self._last_debug_timespan_checkin.add(checker)
		return self.last_debug_timespan

	def _debug_detection_job(self):
		main_thread = threading.main_thread()
		while main_thread.is_alive():
			self.check_debug_detection()
			sleep(0.1)

debug_detector = DebugDetector()

def debug_timespan(checker):
	if utils.debug.is_debug():
		return debug_detector.grab_last_debug_timespan(checker)
	return 0
