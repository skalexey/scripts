import PySide6.QtCore

# Prints PySide6 version
print(PySide6.__version__)

# Prints the Qt version used to compile PySide6
print(PySide6.QtCore.__version__)


# importing libraries
from PySide6.QtWidgets import *
from PySide6 import QtCore, QtGui
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys


class Window(QMainWindow):
	# list of numbers
	number = range(100)

	# desired list
	desired = 32

	def __init__(self, app):
		self.app = app
		screen = app.primaryScreen()
		print('Screen: %s' % screen.name())
		size = screen.size()
		print('Size: %d x %d' % (size.width(), size.height()))
		rect = screen.availableGeometry()
		print('Available: %d x %d' % (rect.width(), rect.height()))
		self.screen_rect = rect;
		super().__init__()

		# setting title
		self.setWindowTitle("Fibonacci Search")

		# setting geometry
		self.setGeometry(0, 0, rect.width(), rect.height())

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()

	def on_desired_text_changed(self, text):
		self.desired = int(text)
		self.result.setText("To search : " + str(self.desired))
	
	def on_delay_text_changed(self, text):
		self.timer.setInterval(int(text))

	# method for widgets
	def UiComponents(self):

		# start flag
		self.start = False

		# divide flag
		self.divide = False
		self.fib_search = True

		# list to hold labels
		self.label_list = []

		# fibonacci numbers
		self.fib1 = 1
		self.fib2 = 0
		self.fib = self.fib1 + self.fib2

		self.offset = -1

		# local counter
		c = 0
		size = len(self.number)
		# iterating list of numbers
		margin_left = 3
		size_per_bar = ( self.screen_rect.width() - margin_left ) / size
		bar_padding = size_per_bar * 0.33
		bar_width = size_per_bar - bar_padding
		for i in self.number:
			# creating label for each number
			label = QLabel(str(i), self)

			# adding background color and border
			label.setStyleSheet("border : 1px solid black; background : white;")

			# aligning the text
			label.setAlignment(Qt.AlignTop)

			# setting geometry using local counter
			# first parameter is distance from left
			# and second is distance from top
			# third is width and fourth is height
			label.setGeometry(margin_left + c * size_per_bar, 50, bar_width, i * 10 + 10)

			# adding label to the label list
			self.label_list.append(label)

			# incrementing local counter
			c = c + 1


		self.input_text_desired = QLineEdit(self)
		self.input_text_desired.setText(str(self.desired))
		self.input_text_desired.setGeometry(100, 200, 100, 30)
		self.input_text_desired.textChanged.connect(self.on_desired_text_changed)

		timer_delay = 300
		self.input_text_delay = QLineEdit(self, str(timer_delay))
		self.input_text_delay.setText(str(self.desired))
		self.input_text_delay.setGeometry(100, 370, 100, 30)
		self.input_text_delay.textChanged.connect(self.on_delay_text_changed)
		self.input_text_delay.setText(str(timer_delay))
		# creating push button to start the search
		self.search_button = QPushButton("Start Search", self)

		# setting geometry of the button
		self.search_button.setGeometry(100, 270, 100, 30)

		# adding action to the search button
		self.search_button.clicked.connect(self.search_action)

		# creating push button to pause the search
		pause_button = QPushButton("Pause", self)

		# setting geometry of the button
		pause_button.setGeometry(100, 320, 100, 30)

		# adding action to the search button
		pause_button.clicked.connect(self.pause_action)

		# creating label to show the result
		self.result = QLabel("To search : " + str(self.desired), self)

		# setting geometry
		self.result.setGeometry(320, 280, 250, 40)

		# setting style sheet
		self.result.setStyleSheet("border : 3px solid black;")

		# adding font
		self.result.setFont(QFont('Times', 10))

		# setting alignment
		self.result.setAlignment(Qt.AlignCenter)

		# creating a timer object
		self.timer = QTimer(self)

		# adding action to timer
		self.timer.timeout.connect(self.showTime)

		# update the timer every 300 millisecond
		self.timer.start(timer_delay)

	# method called by timer
	def showTime(self):

		# checking if flag is true
		if self.start:

			# search fibonacci number
			if self.fib_search:

				# searching for the Fibonacci number greater
				# then the desired number
				if self.fib < len(self.number):

					self.fib2 = self.fib1
					self.fib1 = self.fib
					self.fib = self.fib2 + self.fib1
					self.result.setText("Searching Fibonacci number >=" + str(self.desired))


				# start divide search
				else:
					self.result.setText("Fibonacci found, searching number")
					self.fib_search = False
					self.divide = True


			# start divide search
			if self.divide:

				if self.fib <= 1:
					self.result.setText("Not found")
					self.start = False
					return

				i = min(self.offset + self.fib2, len(self.number) - 1)

				self.label_list[i].setStyleSheet("border : 1px solid black;" "background-color : grey")

				# If desired is greater than the value at
				# index fib2, cut the subarray array
				# from offset to i
				if (self.number[i] < self.desired):
					self.fib = self.fib1
					self.fib1 = self.fib2
					self.fib2 = self.fib - self.fib1
					self.offset = i

				# If desired is greater than the value at
				# index fib2, cut the subarray
				# after i + 1
				elif (self.number[i] > self.desired):
					self.fib = self.fib2
					self.fib1 = self.fib1 - self.fib2
					self.fib2 = self.fib - self.fib1

				# element found. show result and stop search
				else:
					self.result.setText("Found at : " + str(i))
					self.label_list[i].setStyleSheet("border : 2px solid green;" "background-color : lightgreen;")
					self.start = False




	# method called by search button
	def search_action(self):

		# start flag
		self.start = True

		# divide flag
		self.divide = False
		self.fib_search = True

		# fibonacci numbers
		self.fib1 = 1
		self.fib2 = 0
		self.fib = self.fib1 + self.fib2

		self.offset = -1

		# showing text in result label
		self.result.setText("Started searching...")

		for label in self.label_list:
			label.setStyleSheet("border : 1px solid black; background : white;")

	# method called by pause button
	def pause_action(self):

		# making flag false
		self.start = False

		# showing text in result label
		self.result.setText("Paused")


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window(App)

# start the app
sys.exit(App.exec())
