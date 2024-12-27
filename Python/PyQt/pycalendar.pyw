import calendar as py_calendar
import json
import os

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QBrush, QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HolidayCalendar(QMainWindow):
	def __init__(self, year, holiday_data):
		super().__init__()
		self.setWindowTitle(f"Holiday Calendar {year}")
		self.year = year
		self.holiday_data = holiday_data
		self.months_per_row = 3  # Default months per row

		# Main widget and layout
		self.main_widget = QWidget()
		self.main_layout = QVBoxLayout()

		# Year navigation
		self.year_layout = QHBoxLayout()
		self.prev_year_btn = QPushButton("Previous Year")
		self.next_year_btn = QPushButton("Next Year")
		self.year_label = QLabel(str(self.year))
		self.year_label.setAlignment(Qt.AlignCenter)
		self.year_layout.addWidget(self.prev_year_btn)
		self.year_layout.addWidget(self.year_label)
		self.year_layout.addWidget(self.next_year_btn)
		self.main_layout.addLayout(self.year_layout)

		self.prev_year_btn.clicked.connect(self.show_previous_year)
		self.next_year_btn.clicked.connect(self.show_next_year)

		# Add switcher for rows
		self.switcher_layout = QHBoxLayout()
		self.switch_3_btn = QPushButton("3 Months per Row")
		self.switch_4_btn = QPushButton("4 Months per Row")
		self.switcher_layout.addWidget(self.switch_3_btn)
		self.switcher_layout.addWidget(self.switch_4_btn)
		self.main_layout.addLayout(self.switcher_layout)

		self.switch_3_btn.clicked.connect(self.set_3_months_per_row)
		self.switch_4_btn.clicked.connect(self.set_4_months_per_row)

		# Calendar layout
		self.calendar_layout = QGridLayout()
		self.main_layout.addLayout(self.calendar_layout)
		self.main_widget.setLayout(self.main_layout)
		self.setCentralWidget(self.main_widget)

		# Install event filter for theme changes
		self.installEventFilter(self)

		# Populate the calendar
		self.populate_calendar()

	def eventFilter(self, obj, event):
		if event.type() == QEvent.PaletteChange:
			self.populate_calendar()
			return True
		return super().eventFilter(obj, event)

	def show_previous_year(self):
		self.year -= 1
		self.year_label.setText(str(self.year))
		self.populate_calendar()

	def show_next_year(self):
		self.year += 1
		self.year_label.setText(str(self.year))
		self.populate_calendar()

	def set_3_months_per_row(self):
		self.months_per_row = 3
		self.populate_calendar()

	def set_4_months_per_row(self):
		self.months_per_row = 4
		self.populate_calendar()

	def populate_calendar(self):
		# Clear existing layout
		for i in reversed(range(self.calendar_layout.count())):
			widget = self.calendar_layout.itemAt(i).widget()
			if widget:
				widget.setParent(None)

		cal = py_calendar.Calendar()
		palette = self.palette()
		default_text_color = palette.color(QPalette.WindowText)
		holiday_color = palette.color(QPalette.Highlight)
		holiday_text_color = palette.color(QPalette.HighlightedText)
		weekend_color = palette.color(QPalette.AlternateBase)
		faded_color = palette.color(QPalette.Disabled, QPalette.WindowText)

		self.month_widgets = []
		for idx, month in enumerate(range(1, 13)):
			month_label = QLabel(py_calendar.month_name[month])
			month_label.setAlignment(Qt.AlignCenter)

			# Check if the month has any holidays
			month_has_holidays = any(
				key for key in self.holiday_data.keys() if key[0] == self.year and key[1] == month
			)
			if not month_has_holidays:
				month_label.setStyleSheet(f"color: {faded_color.name()};")
				month_label.setDisabled(True)

			self.calendar_layout.addWidget(month_label, (idx // self.months_per_row) * 2, idx % self.months_per_row)

			calendar_table = QTableWidget()
			calendar_table.setColumnCount(7)  # Days of the week
			calendar_table.setHorizontalHeaderLabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
			calendar_table.verticalHeader().setVisible(False)
			calendar_table.setEditTriggers(QTableWidget.NoEditTriggers)
			calendar_table.setSelectionMode(QTableWidget.NoSelection)
			calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit table width
			calendar_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # Adjust row height to content
			if not month_has_holidays:
				calendar_table.setDisabled(True)
				calendar_table.setStyleSheet(f"color: {faded_color.name()};")

			self.calendar_layout.addWidget(calendar_table, (idx // self.months_per_row) * 2 + 1, idx % self.months_per_row)
			self.month_widgets.append(calendar_table)

			month_days = cal.monthdayscalendar(self.year, month)
			calendar_table.setRowCount(len(month_days))

			for row, week in enumerate(month_days):
				for col, day in enumerate(week):
					if day == 0:
						continue

					# Add the day to the table
					item = QTableWidgetItem(str(day))
					item.setTextAlignment(Qt.AlignCenter)

					# Highlight weekends
					if col in (5, 6):  # Saturday and Sunday
						item.setBackground(QBrush(weekend_color))

					# Highlight holidays
					key = (self.year, month, day)
					holiday = self.holiday_data.get(key)
					if holiday:
						item.setBackground(QBrush(holiday_color))
						item.setForeground(QBrush(holiday_text_color))
						item.setToolTip(f"{holiday['name']} ({holiday['status']})")
					calendar_table.setItem(row, col, item)

if __name__ == "__main__":
	app = QApplication([])

	# Load holiday data from a configuration file
	script_dir = os.path.dirname(os.path.abspath(__file__))
	holiday_data_file = os.path.join(script_dir, "holiday_data.json")

	with open(holiday_data_file, "r") as f:
		holiday_data = {
			tuple(map(int, k.split("-"))): v for k, v in json.load(f).items()
		}

	window = HolidayCalendar(2024, holiday_data)
	window.resize(1200, 900)
	window.show()
	app.exec()
