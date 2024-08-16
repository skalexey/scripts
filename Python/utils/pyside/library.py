import math
import os
from abc import ABC

from PySide6.QtCore import QObject, QPoint, QPointF, QRect, QRectF, QSize, QSizeF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
    QGraphicsWidget,
    QInputDialog,
    QLayout,
    QLayoutItem,
    QMessageBox,
    QWidget,
)

import utils  # Lazy import for less important modules
import utils.class_utils as class_utils
import utils.function
import utils.method
from utils.context import GlobalContext
from utils.log.logger import Logger

log = Logger()

# Use EnforcedABCMeta instead of ABCMeta since QtWidget metaclass suppresses the abstractmethod checking behavior
class CombinedMetaQtABC(class_utils.EnforcedABCMeta, type(QWidget)):
	pass


class ABCQt(ABC, metaclass=CombinedMetaQtABC):
	pass


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

spinner_dialog = None

def show_spinner_message(title, message):
	log.info(utils.function.msg_kw())
	global spinner_dialog

	def job():
		global spinner_dialog
		if spinner_dialog is not None:
			spinner_dialog.close()

		spinner_dialog = utils.pyside.widgets.SpinnerDialog()
		spinner_dialog.show()

	return GlobalContext.app.do_in_main_thread(job)

def close_spinner_message():
	log.info(utils.function.msg_kw())
	global spinner_dialog

	def job():
		global spinner_dialog
		if spinner_dialog is not None:
			spinner_dialog.accept()
			spinner_dialog = None

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
	_classes = list(classes)
	if not isinstance(classes[-1], Stub):
		_classes.append(Stub)
	class MixedClass(*_classes):
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
	widget_relative_to = _widget(widget)
	top_left_local = widget_relative_to.mapFromGlobal(rect.topLeft())
	bottom_right_local = widget_relative_to.mapFromGlobal(rect.bottomRight())

	# Create a new QRect from the transformed points
	local_rect = QRect(top_left_local, bottom_right_local)

	return local_rect

def widget(widget):
	if isinstance(widget, QLayoutItem):
		return widget.widget() or parent_widget(widget.layout())
	elif isinstance(widget, QLayout):
		return parent_widget(widget)
	elif isinstance(widget, QWidget):
		return widget
	return None

_widget = widget

def global_to_view_scene_pos(view, global_pos):
	view_pos = view.mapFromGlobal(global_pos)
	scene_pos = view.mapToScene(view_pos)
	return scene_pos

def parent_widget(widget):
	if isinstance(widget, QLayoutItem):
		internals = layout_item_internals(widget)
		return internals.parentWidget()
	return widget.parentWidget()

def global_geometry(widget):
	parent = parent_widget(widget)
	return QRect(parent.mapToGlobal(QPoint(0, 0)), widget.geometry().size())

def global_rect(widget):
	assert widget.size() == widget.rect().size()
	parent = widget.parent()
	return QRect(parent.mapToGlobal(QPoint(0, 0)), widget.size())

def restack_widget(widget, index):
	parent = widget.parentWidget()
	if parent is None:
		raise ValueError("The widget has no parent")

	layout = parent.layout()

	if layout is not None:
		# Widget is managed by a layout
		current_index = layout.indexOf(widget)
		if current_index == -1:
			raise ValueError("The widget is not found in the parent's layout")
		
		# Check if the widget is already at the desired position
		target_index = index if index >= 0 else (layout.count() + index)
		if current_index == target_index:
			return  # Already in the desired position, no need to re-add

		# Detach the widget from the layout and re-add
		layout.takeAt(current_index)
		layout.insertWidget(target_index, widget)
	else:
		# Widget is a direct child of the parent without a layout
		children = parent.children()
		
		target_index = index if index >= 0 else (len(children) + index)
		if children[target_index] == widget:
			return  # Already in the desired position, no need to re-add

		if index != -1 and index < len(children):
			children.remove(widget)
			children.insert(index, widget)

def QSize_gt(size1, size2):
	return size1.width() * size1.height() > size2.width() * size2.height()

def QSize_ge(size1, size2):
	return size1.width() * size1.height() >= size2.width() * size2.height()

def QSize_lt(size1, size2):
	return size1.width() * size1.height() < size2.width() * size2.height()

def QSize_le(size1, size2):
	return size1.width() * size1.height() <= size2.width() * size2.height()

def QSizeF_eq(size1, size2):
	return math.isclose(size1.width(), size2.width()) and math.isclose(size1.height(), size2.height())

def QSizeF_div(size1, size2):
	return QSizeF(size1.width() / size2.width(), size1.height() / size2.height())

def QSizeF_mul(size1, size2):
	return QSizeF(size1.width() * size2.width(), size1.height() * size2.height())

def QPointF_mul_size(point, size):
	return QPointF(point.x() * size.width(), point.y() * size.height())

def QRectF_mul_size(rect, size):
	top_left = QPointF_mul_size(rect.topLeft(), size)
	size = QSizeF_mul(rect.size(), size)
	return QRectF(top_left, size)

def foreach_internals(widget, func, depth=0, max_depth=None):
	if max_depth is not None and depth >= max_depth:
		return

	def go_deeper(child):
		foreach_internals(child, func, depth+1, max_depth)

	if isinstance(widget , QLayout):
		for i in range(widget.count()):
			child = widget.itemAt(i)
			func(child)
			go_deeper(child)
	elif isinstance(widget, QLayoutItem):
		child = layout_item_internals(widget)
		func(child)
		go_deeper(child)
	elif isinstance(widget, QGraphicsWidget):
		children = widget.childItems()
		for child in children:
			func(child)
			go_deeper(child)
	else:
		children_attr = getattr(widget, "children", None)
		if children_attr is not None:
			assert isinstance(widget, (QWidget, QObject))
			assert callable(children_attr)
			children = children_attr()
			for child in children:
				func(child)
				go_deeper(child)
			return

def layout_item_internals(layout_item):
	return layout_item.widget() or layout_item.layout()

def foreach_not_hidden_child(widget, func, *args, **kwargs):
	def job(child):
		if isinstance(child, QLayout):
			foreach_internals(child, job, max_depth=1)
			return
		is_hidden_attr = getattr(child, "isHidden", None)
		if is_hidden_attr is not None:
			if is_hidden_attr():
				return
		else:
			is_visible_attr = getattr(child, "isVisible", None)
			if is_visible_attr is not None:
				if not is_visible_attr():
					return
		func(child)
	foreach_internals(widget, job, *args, **kwargs)

def geometry(widget):
	if isinstance(widget, QGraphicsItem):
		return QRectF(widget.pos(), widget.boundingRect().size())
	else:
		return widget.geometry()

def children_geometry(widget):
	if isinstance(widget, QWidget):
		return widget.childrenRect() # It does effectively the same as the code below, but more efficiently since it is a native call
	result = None
	def job(child):
		nonlocal result
		child_geometry = geometry(child)
		result = result.united(child_geometry) if result is not None else child_geometry
	foreach_not_hidden_child(widget, job, max_depth=1)
	return result or QRect()

def foreach_geometry_influencer(widget, func):
	def job(child):
		contents_geom = children_geometry(child)
		rect = child.rect() if hasattr(child, "rect") else QRect(QPoint(0, 0), child.geometry().size())
		if rect.contains(contents_geom):
			func(child)
		else:
			foreach_geometry_influencer(child, func)
	foreach_not_hidden_child(widget, job)

def collect_geometry_influencers(widget):
	result = []
	def job(child):
		result.append(child)
	foreach_geometry_influencer(widget, job)
	return result

def collect_not_hidden_children(widget):
	result = []
	def job(child):
		result.append(child)
	foreach_not_hidden_child(widget, job)
	return result

def qcolor(color):
	if isinstance(color, str):
		return QColor(color)
	elif isinstance(color, QColor):
		return color
	return None
