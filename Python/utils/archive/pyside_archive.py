def ask_yes_no(title, message, on_answer=None, yes_text=None, no_text=None):	
	# Simplified version, but without customization:
	# result = QMessageBox.question(None, title, message)
	# if result == QMessageBox.Yes:
	# 	on_yes()
	# else:
	# 	on_no()

def show_message(title, message):
	log.info(f"Show message: {title}, {message}")
	# msg_box = QMessageBox()
	# msg_box.setIcon(QMessageBox.Information)
	# msg_box.setWindowTitle(title)
	# msg_box.setText(message)
	# msg_box.setStandardButtons(QMessageBox.Ok)

	# future = concurrent.futures.Future()
	# def _on_confirm():
	# 	future.set_result(True)
	# 	if on_confirm is not None:
	# 		on_confirm()
	# msg_box.buttonClicked.connect(lambda: _on_confirm())
	# msg_box.exec_()
	# return future
	return QMessageBox.information(None, title, message)





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
    QListWidget,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

import utils.function
import utils.method
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
		msg_box.exec()

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
# V1
def WidgetBase(*classes):
	class WidgetBase(*classes):
		def __init__(self, parent=None, parent_layout=None, *args, **kwargs):
			if parent_layout is not None and parent is not None:
				raise ValueError(utils.method.msg("ResourceListWidget: parent and parent_layout cannot be both set"))
			super().__init__(parent, *args, **kwargs)
			if parent_layout is not None:
				parent_layout.addWidget(self)
	return WidgetBase


# V2
def WidgetBase(*classes):
	class WidgetBase(*classes):
		# Support using Qt signatures directly like QPushButton("Click", parent)
		def __init__(self, *args, parent=NoValue, parent_layout=None, **kwargs):
			if parent is not NoValue: # Need to distinguish between not passed parent and explicitly passed None as a parent
				# Expect multiple values error from Qt in the case of provided parent in *args as well.
				kwargs["parent"] = parent
			if parent_layout is not None: # Exclude any additional parameters except provided for Qt __init__ variations that don't carry-over the arguments.
				kwargs["parent_layout"] = parent_layout
			if parent_layout is not None and parent:
				raise ValueError(utils.method.msg("ResourceListWidget: parent and parent_layout cannot be both set"))
			# Expect Qt errors in the case of provided both kwargs and several positional arguments.
			super().__init__(*args, **kwargs)
			if parent_layout is not None:
				parent_layout.addWidget(self)
	return WidgetBase


# class CombinedMeta(type(QLabel), type(AbstractTextSpinner)):
# 	pass


base = AbstractTextSpinner(QLabel)
class TextSpinner(base):
	def __init__(self, parent=None, *args, **kwargs):
		super().__init__(parent, *args, **kwargs)
		self.setAlignment(Qt.AlignCenter)

	@base.text.getter
	def text(self):
		return self.text()

	@base.text.setter
	def text(self, value):
		self.setText(value)

class CopyableMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def contextMenuEvent(self, event):
		item = self.itemAt(event.pos())
		if item:
			context_menu = QMenu(self)
			copy_action = QAction("Copy", self)
			context_menu.addAction(copy_action)
			item_text = item.text()
			copy_action.triggered.connect(lambda: self.copy_item_content(item_text))
			context_menu.exec(event.globalPos())

	def copy_item_content(self, text):
		clipboard = QApplication.clipboard()
		clipboard.setText(text)

class CopyableLabel(WidgetBase(CopyableMixin, QLabel)):
	def __init__(self, text="", parent=None, *args, **kwargs):
		super().__init__(text, parent, *args, **kwargs)
		self.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Enable text selection
		self.setContextMenuPolicy(Qt.CustomContextMenu)  # Enable custom context menu
		self.customContextMenuRequested.connect(self.show_context_menu)

	def show_context_menu(self, pos):
		context_menu = QMenu(self)
		copy_action = QAction("Copy", self)
		copy_action.triggered.connect(self.copy_text)
		context_menu.addAction(copy_action)
		context_menu.exec(self.mapToGlobal(pos))

	def copy_text(self):
		clipboard = QApplication.clipboard()
		clipboard.setText(self.text())


class ValueWidget(WidgetBase(QWidget)):
	def __init__(self, label, value, fixed_width=None, value_fixed_width=None, parent=None, parent_layout=None, *args, **kwargs):
		super().__init__(parent=parent, parent_layout=parent_layout, *args, **kwargs)
		layout = QHBoxLayout()
		self.setLayout(layout)
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		# Label
		label_widget = QLabel(label)
		layout.addWidget(label_widget)
		# Value
		self.value_label = CopyableLabel(str(value))
		if value_fixed_width is not None:
			self.value_label.setFixedWidth(value_fixed_width)
		layout.addWidget(self.value_label)

	def set_value(self, value):
		self.value_label.setText(str(value))

	def value(self):
		return self.value_label.text()


class ExpandableWidget(WidgetBase(QWidget)):
	def __init__(self, title=None, expanded_widget=None, collapsed_widget=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Layouting
		layout = QVBoxLayout()
		self.setLayout(self.layout)
		self.hlayout = QHBoxLayout()
		self.hlayout.setAlignment(Qt.AlignLeft)
		layout.addLayout(self.hlayout)
		# Widgets
		self.collapsed_widget = collapsed_widget or QLabel(title or "")
		self.hlayout.addWidget(self.collapsed_widget)
		self.expanded_widget = expanded_widget
		if self.expanded_widget is not None:
			layout.addWidget(self.expanded_widget)
		# Expand button
		self.expand_button = QPushButton("+")
		self.expand_button.clicked.connect(self._on_expand_click)
		self.hlayout.addWidget(self.expand_button)
		self.update()

	def _on_expand_click(self):
		self.expand()

	def _on_collapse_click(self):
		self.collapse()

	def expand(self):
		self.expand_button.setText("-")
		self.expand_button.clicked.disconnect()
		self.expand_button.clicked.connect(self._on_collapse_click)
		if self.expanded_widget is not None:
			self.expanded_widget.show()

	def collapse(self):
		self.expand_button.setText("+")
		self.expand_button.clicked.disconnect()
		self.expand_button.clicked.connect(self._on_expand_click)
		if self.expanded_widget is not None:
			self.expanded_widget.hide()


class FitContentsMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.adjustSize()

	def addItem(self, item_text):
		# item = QListWidgetItem(item_text)
		# item.setSizeHint(QSize(self.fontMetrics().horizontalAdvance(item_text) + 20, self.fontMetrics().height() + 10))
		super().addItem(item_text)
		self.adjustSizeToContents()

	def adjustSizeToContents(self):
		total_width = max(self.sizeHintForColumn(0) + self.verticalScrollBar().sizeHint().width(), self.width())
		total_height = self.sizeHintForRow(0) * self.count() + self.horizontalScrollBar().sizeHint().height()
		self.setFixedSize(total_width, total_height)


class CopyableMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def contextMenuEvent(self, event):
		item = self.itemAt(event.pos())
		if item:
			context_menu = QMenu(self)
			copy_action = QAction("Copy", self)
			context_menu.addAction(copy_action)
			item_text = item.text()
			copy_action.triggered.connect(lambda: self.copyItemContent(item_text))
			context_menu.exec(event.globalPos())

	def copyItemContent(self, text):
		clipboard = QApplication.clipboard()
		clipboard.setText(text)


class ResizableListWidget(WidgetBase(FitContentsMixin, CopyableMixin, QListWidget)):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.adjustSize()


def children_geometry(widget):
	log.debug(utils.function.msg_kw())
	geometry = None
	def job(child):
		nonlocal geometry
		if isinstance(child, QLayout):
			foreach_internals(child, job, max_depth=1)
			return
		if not hasattr(child, "geometry"):
			return
		if hasattr(child, "isHidden"):
			if child.isHidden():
				log.debug(f"Child {child} is hidden. Its geometry will be ignored, but here it is: {child.geometry()}.")
				return
		
		child_geometry = child.geometry()
		# child_geometry = QRect(child.pos(), child.size()) if hasattr(child, "size") else child.geometry()
		# Parent check is not used by widget.childrenRect()
		# child_parent = child.parent()
		# parent_rect = child_parent.rect() if hasattr(child.parent(), "rect") else QRect(QPoint(0, 0), child.parent().geometry().size())
		# if isinstance(child_parent, QWidget):
		# 	if not parent_rect.contains(child_geometry):
		# 		log.debug(f"Child {child} geometry {child_geometry} is not contained in its parent {child.parent()} rect {parent_rect}. Ignore it")
		# 	# Clamp the child geometry to the parent rect
		# 	child_geometry = child_geometry.intersected(parent_rect)
		child_text_addition = f" text: '{child.text()}" if hasattr(child, "text") else ""
		log.debug(f"Child {child} geometry: {child_geometry}{child_text_addition}")
		geometry = geometry.united(child_geometry) if geometry is not None else child_geometry
	foreach_internals(widget, job, max_depth=1)
	# qt_contents_geom = widget.contentsRect()
	# assert geometry == qt_contents_geom
	geometry = geometry or QRect()
	if hasattr(widget, "childrenRect"):
		qt_children_rect = widget.childrenRect()
		assert geometry == qt_children_rect
	v1 = children_geometry_v1(widget)
	if v1 != geometry:
		children_geometry(widget)
	assert geometry == v1
	return geometry

def foreach_internals_layouts_widgets(widget, func, depth=0, max_depth=None):
	if max_depth is not None and depth >= max_depth:
		return

	def go_deeper(child):
		foreach_internals_layouts_widgets(child, func, depth+1, max_depth)

	if isinstance(widget, QWidget):
		children = widget.children()
		for child in children:
			func(child)
			go_deeper(child)
	elif isinstance(widget, QLayout):
		for i in range(widget.count()):
			child = widget.itemAt(i)
			func(child)
			go_deeper(child)
	elif isinstance(widget, QLayoutItem):
		child = layout_item_internals(widget)
		func(child)
		go_deeper(child)