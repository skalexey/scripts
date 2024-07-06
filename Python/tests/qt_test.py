from test import *

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
)
from utils.profile.trackable_resource import TrackableResource
from utils.pyside import WidgetBase


def TrackableWidget(base_class):
	class TrackableWidget(WidgetBase(TrackableResource, base_class)):
		pass
	return TrackableWidget

def circular_ref_test():
	log(title("Circular Reference Test"))
	app = QApplication([])
	window = QMainWindow()
	window.setWindowTitle("Circular Reference Test")
	label = QLabel("Hello, World!")
	button = QPushButton("Click me!")

	window.setCentralWidget(label)
	window.setCentralWidget(button)

	class Composition(TrackableResource):
		def __init__(self, parent):
			super().__init__()
			assert_exception('self.button = TrackableWidget(QPushButton)("Click me!", parent, parent=parent)')
			self.layout = QVBoxLayout(parent)
			self.button = TrackableWidget(QPushButton)("Click me!", parent)
			self.button.clicked.connect(self.on_click)

		def on_click(self):
			print("Button clicked")


	class ConnectedWidget(WidgetBase(TrackableResource, QPushButton)):
		def __init__(self):
			super().__init__()
			self.clicked.connect(self.on_click)

		def on_click(self):
			print("Button clicked")

	def closed_scope(window):
		c = Composition(window)
		# w = EmptyWidget(window)
		# w.show()
		# w.deleteLater()


	closed_scope(window)

	window.show()
	app.exec()
	log(title("End of Circular Reference Test"))

def qt_test():
	circular_ref_test()

def test():
	log(title("Qt Test"))
	qt_test()
	log(title("End of Qt Test"))

run()
