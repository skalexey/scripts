import os
from utils.log import *
from PySide6.QtWidgets import QFileDialog, QMessageBox

logger = Logger("pyside")

def select_data_file():
	file_dialog = QFileDialog()
	file_dialog.setFileMode(QFileDialog.ExistingFiles)
	file_dialog.setNameFilter("CSV files (*.csv)")
	file_dialog.setDirectory("data")
	if file_dialog.exec():
		selected_files = file_dialog.selectedFiles()
		current_directory = os.getcwd()
		file_path1 = os.path.relpath(selected_files[0], current_directory)
		logger.log_info(f"Selected quote data file: {file_path1}")
		if len(selected_files) == 2:
			file_path2 = os.path.relpath(selected_files[1], current_directory)
			logger.log_info(f"Selected trading data file: {file_path2}")
		else:
			file_path2 = None
		return file_path1, file_path2
	return None, None

def show_message(title, message):
	logger.log_info(f"Show message: {title}, {message}")
	QMessageBox.information(None, title, message)
