import os

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QSlider,
    QWidget,
)

from utils.log.logger import *

log = Logger("pyside")

def select_data_file():
	file_dialog = QFileDialog()
	file_dialog.setFileMode(QFileDialog.ExistingFiles)
	file_dialog.setNameFilter("CSV files (*.csv)")
	file_dialog.setDirectory("data")
	if file_dialog.exec():
		selected_files = file_dialog.selectedFiles()
		current_directory = os.getcwd()
		file_path1 = os.path.relpath(selected_files[0], current_directory)
		log.info(f"Selected quote data file: {file_path1}")
		if len(selected_files) == 2:
			file_path2 = os.path.relpath(selected_files[1], current_directory)
			log.info(f"Selected trading data file: {file_path2}")
		else:
			file_path2 = None
		return file_path1, file_path2
	return None, None

def show_message(title, message):
	log.info(f"Show message: {title}, {message}")
	QMessageBox.information(None, title, message)

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
	slider.valueChanged.connect(on_changed)
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