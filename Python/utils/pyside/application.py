import concurrent.futures
import threading
from datetime import datetime

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtWidgets import QApplication


class Application(QApplication):
	class JobEvent(QEvent):
		TYPE = QEvent.Type(QEvent.registerEventType())
		def __init__(self, func):
			super().__init__(self.TYPE)
			self.func = func

	def __init__(self, context, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.context = context
		self._post_event_lock = threading.Lock()
		update_interval = 1 / 60  # 60 FPS
		# Run a global update loop in Qt thread
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(update_interval * 1000)  # Update every 1000 milliseconds (1 second)
		self.last_time = None
		self.installEventFilter(self)

	def eventFilter(self, obj, event):
		if event.type() == Application.JobEvent.TYPE:
			event.func()
			return True
		return super().eventFilter(obj, event)

	def do_in_main_thread(self, func):
		main_thread = threading.main_thread()
		if threading.current_thread() == main_thread:
			return func()
		future = concurrent.futures.Future()
		def job():
			result = func()
			future.set_result(result)
		with self._post_event_lock:
			event = Application.JobEvent(job)
			QApplication.postEvent(self, event)
		return future

	def update(self):
		current_time = self.context.current_time()
		dt = current_time - (self.last_time or current_time)
		self.last_time = current_time
		current_datetime = datetime.fromtimestamp(current_time)
		last_datetime = datetime.fromtimestamp(self.last_time)
		# log.debug(f"last_time: {self.last_time}, current_time: {current_time}, dt: {dt}, last_datetime: {last_datetime}, current_datetime: {current_datetime}")
		self.context.module_manager.call_on_modules("on_update", dt)
