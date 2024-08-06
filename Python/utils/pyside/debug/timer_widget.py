import sys
import traceback

from PySide6.QtCore import QCoreApplication, QEventLoop, QThread, QTimer
from PySide6.QtNetwork import QNetworkAccessManager
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


def print_stack():
	print("Called from thread:", QThread.currentThread())
	for line in traceback.format_stack():
		print(line.strip())

class TimerDebugWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.init_ui()
		self.setup_debugging()

	def init_ui(self):
		layout = QVBoxLayout()
		self.button = QPushButton("Start Timer", self)
		self.button.clicked.connect(self.start_timer)
		layout.addWidget(self.button)
		self.setLayout(layout)

	def start_timer(self):
		print_stack()
		timer = QTimer()
		timer.timeout.connect(lambda: print("Timer timeout"))
		timer.start(1000)

	def setup_debugging(self):
		# Override QThread methods to print call stack
		original_msleep = QThread.msleep
		original_sleep = QThread.sleep
		original_usleep = QThread.usleep

		def debug_msleep(ms):
			print_stack()
			original_msleep(ms)

		def debug_sleep(s):
			print_stack()
			original_sleep(s)

		def debug_usleep(us):
			print_stack()
			original_usleep(us)

		QThread.msleep = debug_msleep
		QThread.sleep = debug_sleep
		QThread.usleep = debug_usleep

		# Override QNetworkAccessManager
		original_get = QNetworkAccessManager.get

		def debug_get(request):
			print_stack()
			return original_get(self, request)

		QNetworkAccessManager.get = debug_get

		# Override QCoreApplication::processEvents
		original_process_events = QCoreApplication.processEvents

		def debug_process_events(flags=QEventLoop.AllEvents, maxtime=-1):
			print_stack()
			original_process_events(flags, maxtime)

		QCoreApplication.processEvents = debug_process_events

if __name__ == "__main__":
	app = QApplication(sys.argv)
	widget = TimerDebugWidget()
	widget.show()
	sys.exit(app.exec())
