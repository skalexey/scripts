import os

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

import utils.function
import utils.method
from utils.context import GlobalContext
from utils.lang import NoValue
from utils.log.logger import Logger

log = Logger()

def select_data_file(dir=None):
	file_dialog = QFileDialog()
	file_dialog.setFileMode(QFileDialog.ExistingFiles)
	file_dialog.setNameFilter("CSV files (*.csv)")
	if dir is not None:
		file_dialog.setDirectory(dir)
	if file_dialog.exec():
		selected_files = file_dialog.selectedFiles()
		file_path1 = os.path.relpath(selected_files[0])
		log.info(f"Selected quote data file: {file_path1}")
		if len(selected_files) == 2:
			file_path2 = os.path.relath(selected_files[1])
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
		msg_box.exec()

		return state.result

	return GlobalContext.app.do_in_main_thread(job)

def show_input_dialog(title, message, on_answer):
	text, ok = QInputDialog.getText(None, title, message)
	if ok:
		on_answer(text)

class Stub:
	# This class allows to carry over the same arguments through all the mixins passing QWidget if it is the last in the chain since QWidget needs to resolve the remaining arguments against the 'object' class.
	def __init__(self, *args, parent_layout=None, parent=None, **kwargs):
		super().__init__(*args, **kwargs)

def WidgetBase(*classes):
	# See the comments above of Stub class purpose.
	# If not Stub is set, expect Qt errors in the case of provided both kwargs and several positional arguments. Qt performs the checks after super().__init__ call.
	# Adding also allows to better diagnose problems caused by passing excessive arguments.
	class WidgetBase(*classes, Stub):
		# Support using Qt signatures directly like QPushButton("Click", parent)
		def __init__(self, *args, parent_layout=None, **kwargs):
			if parent_layout is not None and kwargs.get("parent") is not None:
				raise ValueError(utils.method.msg("ResourceListWidget: parent and parent_layout cannot be both set"))
			super().__init__(*args, **kwargs, parent_layout=parent_layout) # Carry over parent_layout to all the mixins
			if parent_layout is not None:
				parent_layout.addWidget(self)
	return WidgetBase

def mixed_class(*classes):
	# See the comments above of Stub class purpose.
	class MixedClass(*classes, Stub):
		pass
	return MixedClass


def clamp_geometry(widget, clamper_widget, geometry=None):
	# Transform into screen space first
	r1 = geometry or widget.geometry()
	r2 = clamper_widget.geometry()
	r1 = map_to_global(widget, r1)
	r2 = map_to_global(clamper_widget, r2)
	# Calculate the intersection
	intersection = r1.intersected(r2)
	# Transform back to the widget space
	intersection = map_from_global(widget, intersection)
	return intersection

def map_to_global(widget, rect):
	"""
	Transform a QRect from the local coordinate space of a widget to the global coordinate space.

	:param widget: The widget whose coordinate space the QRect is in.
	:param rect: The QRect to transform.
	:return: A new QRect in the global coordinate space.
	"""
	# Transform the top-left and bottom-right corners to global coordinates
	top_left_global = widget.mapToGlobal(rect.topLeft())
	bottom_right_global = widget.mapToGlobal(rect.bottomRight())

	# Create a new QRect from the transformed points
	global_rect = QRect(top_left_global, bottom_right_global)

	return global_rect

def map_from_global(widget, rect):
	"""
	Transform a QRect from the global coordinate space to the local coordinate space of a widget.

	:param widget: The widget whose coordinate space the QRect will be transformed into.
	:param rect: The QRect in global coordinates.
	:return: A new QRect in the local coordinate space of the widget.
	"""
	# Transform the top-left and bottom-right corners from global coordinates to local coordinates
	top_left_local = widget.mapFromGlobal(rect.topLeft())
	bottom_right_local = widget.mapFromGlobal(rect.bottomRight())

	# Create a new QRect from the transformed points
	local_rect = QRect(top_left_local, bottom_right_local)

	return local_rect
