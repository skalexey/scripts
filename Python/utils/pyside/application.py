import concurrent.futures
import sys
import threading
from datetime import datetime

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtWidgets import QApplication

import utils.debug.debug_detector
from utils.collection.associative_list import AssociativeList
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger
from utils.subscription import Subscription

log = Logger()

class Application(QApplication):
	class JobEvent(QEvent):
		TYPE = QEvent.Type(QEvent.registerEventType())
		def __init__(self, func):
			super().__init__(self.TYPE)
			self.func = func

	def __init__(self, context, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.context = context
		self._post_event_lock = wrap_debug_lock(threading.Lock())
		update_interval = 1 / 60  # 60 FPS
		self.dt_limit = sys.maxsize # TODO: Tests. Move to settings. Remove from Live config
		# Run a global update loop in Qt thread
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(update_interval * 1000)  # Update every 1000 milliseconds (1 second)
		self._last_time = None
		self._time_lock = wrap_debug_lock(threading.RLock())
		self.on_time_invalidated = Subscription()
		self.on_update_jobs = AssociativeList()
		self.installEventFilter(self)

	@property
	def last_time(self):
		with self._time_lock:
			return self._last_time

	@last_time.setter
	def last_time(self, value):
		with self._time_lock:
			self._last_time = value
			if value is None:
				log.debug(utils.method.msg_kw("Time has been invalidated"))
				self.on_time_invalidated()

	def eventFilter(self, obj, event):
		if event.type() == Application.JobEvent.TYPE:
			event.func()
			return True
		return super().eventFilter(obj, event)

	def do_in_main_thread(self, func, *args, **kwargs):
		main_thread = threading.main_thread()
		if threading.current_thread() == main_thread:
			return func()
		future = concurrent.futures.Future()
		def job():
			result = func(*args, **kwargs)
			future.set_result(result)
		with self._post_event_lock:
			event = Application.JobEvent(job)
			QApplication.postEvent(self, event)
		return future

	def add_on_update(self, func):
		self.on_update_jobs.add(func)

	def on_update(self, dt):
		self.context.module_manager.call_on_modules("on_update", dt)

	def update(self):
		current_time = self.context.current_time()
		dt = min(current_time - (self.last_time or current_time), self.dt_limit)
		jobs_to_delete = []
		for id, job in self.on_update_jobs:
			if job(dt) is False:
				jobs_to_delete.append(id)
		for id in jobs_to_delete:
			self.on_update_jobs.remove(id)
		self.last_time = current_time
		self.on_update(dt)

	def check_debug_timespan(self):
		debug_timespan = utils.debug.debug_detector.debug_timespan(self)
		if debug_timespan != 0:
			log.debug(utils.method.msg_kw(f"Debug timespan: {debug_timespan}"))
			self.last_time = None
			return True
		return False

	def current_datetime(self):
		self.check_debug_timespan()
		return datetime.now()
