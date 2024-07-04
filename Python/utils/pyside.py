import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QClipboard
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QSizePolicy,
    QSlider,
    QWidget,
)

import utils.function
from utils.context import GlobalContext
from utils.log.logger import Logger
from utils.text import AbstractTextSpinner

log = Logger()

def select_data_file(dir=None):
	file_dialog = QFileDialog()
	file_dialog.setFileMode(QFileDialog.ExistingFiles)
	file_dialog.setNameFilter("CSV files (*.csv)")
	if dir is not None:
		file_dialog.setDirectory(dir)
	if file_dialog.exec():
		selected_files = file_dialog.selectedFiles()
		file_path1 = os.path.abspath(selected_files[0])
		log.info(f"Selected quote data file: {file_path1}")
		if len(selected_files) == 2:
			file_path2 = os.path.abspath(selected_files[1])
			log.info(f"Selected trading data file: {file_path2}")
		else:
			file_path2 = None
		return file_path1, file_path2
	return None, None

# Every message box blocks the calling thread, and it must be processed in the main thread.
def show_message(title, message):
	log.info(utils.function.msg_kw())

	def job():
		return QMessageBox.information(None, title, message)

	return GlobalContext.app.do_in_main_thread(job)

def attention_message(title=None, message=None):
	_title = title or "Attention"
	log.attention(utils.function.msg_kw())

	def job():
		return QMessageBox.warning(None, _title, message)

	return GlobalContext.app.do_in_main_thread(job)

def ask_yes_no(title, message, on_answer=None, yes_text=None, no_text=None):
	log.info(utils.function.msg_kw())

	def job():
		msg_box = QMessageBox()
		msg_box.setIcon(QMessageBox.Question)
		msg_box.setWindowTitle(title)
		msg_box.setText(message)
		msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		_yes_text = "Yes"
		if yes_text is not None:
			msg_box.setButtonText(QMessageBox.Yes, yes_text)
			_yes_text = yes_text
		if no_text is not None:
			msg_box.setButtonText(QMessageBox.No, no_text)

		class State:
			def __init__(self):
				self.result = None
		state = State()

		def _on_answer(button):
			button_text = button.text()
			state.result = button_text.lower().find(_yes_text.lower()) != -1

		msg_box.buttonClicked.connect(_on_answer)
		msg_box.exec_()

		return state.result

	return GlobalContext.app.do_in_main_thread(job)

def show_input_dialog(title, message, on_answer):
	text, ok = QInputDialog.getText(None, title, message)
	if ok:
		on_answer(text)

def create_slider_input_widget(parent_layout, label, min_value, max_value, default_value, on_changed, slider_fixed_width=None):
	widget = QWidget()
	layout = QHBoxLayout()
	parent_layout.addWidget(widget)
	widget.setLayout(layout)
	label_widget = QLabel(label)
	layout.addWidget(label_widget)
	slider = QSlider(Qt.Horizontal)
	slider.setMinimum(min_value)
	slider.setMaximum(max_value)
	slider.setValue(default_value)
	if slider_fixed_width is not None:
		slider.setFixedWidth(slider_fixed_width)
	layout.addWidget(slider)
	value_label = QLabel(str(default_value))
	layout.addWidget(value_label)
	def on_value_changed(value):
		value_label.setText(str(value))
		on_changed(value)
	slider.valueChanged.connect(on_value_changed)
	return widget, slider, value_label

def create_line_input_widget(parent_layout, label, default_value=None, on_changed=None, input_fixed_width=None):
	widget = QWidget()
	layout = QHBoxLayout()
	parent_layout.addWidget(widget)
	widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
	widget.setLayout(layout)
	label_widget = QLabel(label)
	layout.addWidget(label_widget)
	line_edit = QLineEdit()
	if default_value is not None:
		t = type(default_value)
		assert t is str or t is int or t is float or t is bool
		line_edit.setText(str(default_value))
	if input_fixed_width is not None:
		line_edit.setFixedWidth(input_fixed_width)
	layout.addWidget(line_edit)
	if on_changed is not None:
		def on_text_changed(text):
			on_changed(text)
		line_edit.textChanged.connect(on_text_changed)
	return widget, line_edit

def create_checkbox_widget(parent_layout, label, default_value, on_changed):
	widget = QWidget()
	layout = QHBoxLayout()
	parent_layout.addWidget(widget)
	widget.setLayout(layout)
	checkbox = QCheckBox(label)
	checkbox.setChecked(default_value)
	layout.addWidget(checkbox)
	def on_state_changed(state):
		on_changed(state == Qt.Checked.value)
	checkbox.stateChanged.connect(on_state_changed)
	return widget, checkbox

class CombinedMeta(type(QLabel), type(AbstractTextSpinner)):
	pass
		
class TextSpinner(AbstractTextSpinner, QLabel, metaclass=CombinedMeta):
	def __init__(self, parent=None):
		QLabel.__init__(self, parent)
		self.setAlignment(Qt.AlignCenter)
		AbstractTextSpinner.__init__(self)

	@AbstractTextSpinner.text.getter
	def text(self):
		return self.text()

	@AbstractTextSpinner.text.setter
	def text(self, value):
		self.setText(value)
