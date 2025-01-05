from PySide6.QtCore import QEvent, QTimer
from PySide6.QtWidgets import QApplication

from utils.application import Application as ABCApplication
from utils.log.logger import Logger
from utils.pyside import CombinedMetaQtABC

log = Logger()


class Application(ABCApplication, QApplication, metaclass=CombinedMetaQtABC):
	"""
	Qt implementation for utils.Application class. Defines update loop handling logic through QTimer, and integrates Qt's quit() method.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.update_interval * 1000)  # Update every 1000 milliseconds (1 second)
		self.installEventFilter(self)
		# Setup the quit signal handler for the application
		
		self.aboutToQuit.connect(self._on_about_to_quit)

	def _on_about_to_quit(self):
		log("Application is about to quit.")
		super().stop()

	# Application.stop override
	def stop(self):
		super().stop()
		self.quit()

	# Qt's exit
	def quit(self):
		super().quit()

	def eventFilter(self, obj, event):
		# Uncomment if you need a custom event processing	
		# if event.type() == Application.SomeEvent.TYPE:
		# 	event.func()
		# 	return True
		return super().eventFilter(obj, event)

	# Uncomment if you need a custom event processing
	# class SomeEvent(QEvent):
	# 	TYPE = QEvent.Type(QEvent.registerEventType())
	# 	def __init__(self, func):
	# 		super().__init__(self.TYPE)
	# 		self.func = func
