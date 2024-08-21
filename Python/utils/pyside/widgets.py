import types
from abc import abstractmethod

from PySide6.QtCore import (
    QChildEvent,
    QEvent,
    QLineF,
    QObject,
    QRect,
    QSize,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QGraphicsLineItem,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import utils.lang
import utils.method
import utils.pyside
from utils.collection.ordered_dict import OrderedDict
from utils.collection.weak_list import WeakList
from utils.lang import NoValue
from utils.live import verify
from utils.log.logger import Logger
from utils.math.range import Range
from utils.memory import SmartCallable
from utils.pyside import ABCQt, CombinedMetaQtABC, WidgetBase
from utils.pyside.auto_layout import (
    AutoLayout,  # For importing it from utils.pyside.widgets
)
from utils.subscription import Subscription
from utils.text import AbstractTextSpinner

log = Logger()


class AbstractWidget(ABCQt):
	on_resized = Signal(QWidget, QSize)
	on_child_added = Signal(QWidget)
	on_child_removed = Signal(QWidget)
	on_parent_changed = Signal(QWidget)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._on_contents_changed()

	def adjust_size(self, geometry=None):
		if geometry is not None:
			self.setGeometry(geometry)
			# self._on_resized(geometry.size()) # V0 impl
		else:
			self.adjustSize()
			# self._on_resized(self.geometry().size()) # V0 impl

	def _on_parent_changed(self, parent):
		self.on_parent_changed.emit(self)

	def _on_resized(self, size):
		self.on_resized.emit(self, size)

	def _on_child_added(self, child):
		self.on_child_added.emit(child)

	def _on_child_removed(self, child):
		self.on_child_removed.emit(child)

	def _on_contents_changed(self):
		self.adjust_size()

	def update(self, dt=None, *args, **kwargs):
		pass
		# self._on_contents_changed() # TODO: consider lighter options
		# super().update(*args, **kwargs)

	def event(self, event):
		if event.type() == QEvent.ParentChange:
			self._on_parent_changed(self.parent())
		elif event.type() == QEvent.ChildAdded:
			child_event = QChildEvent(event)
			log.verbose(utils.method.msg_kw(f"Child added: {child_event.child()}"))
			self._on_child_added(child_event.child())
		elif event.type() == QEvent.ChildRemoved:
			log.verbose(utils.method.msg_kw(f"Child removed: {event.child()}"))
			self._on_child_removed(event.child())
		elif event.type() == QEvent.Resize:
			log.verbose(utils.method.msg_kw(f"Resized: {self.geometry().size()}")) # assert event.size() == self.geometry().size()
			self._on_resized(self.geometry().size())
		elif event.type() == QEvent.Move:
			log.verbose(utils.method.msg_kw(f"Moved: {self.geometry().topLeft()}"))
		return super().event(event)


class SliderInputWidget(WidgetBase(QWidget)):
	def __init__(self, label, min_value, max_value, default_value, on_changed=None, slider_fixed_width=None, value_label_fixed_width=None, fixed_width=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.set_on_value_changed(on_changed)
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		layout = QHBoxLayout()
		self.setLayout(layout)
		_label_widget = QLabel(label) if isinstance(label, str) else label
		layout.addWidget(_label_widget)
		self.slider = QSlider(Qt.Horizontal)
		self.slider.setMinimum(min_value)
		self.slider.setMaximum(max_value)
		self.slider.setValue(default_value)
		if slider_fixed_width is not None:
			self.slider.setFixedWidth(slider_fixed_width)
		layout.addWidget(self.slider)
		self.value_label = QLabel(str(default_value))
		if value_label_fixed_width is not None:
			self.value_label.setFixedWidth(value_label_fixed_width)
		layout.addWidget(self.value_label)
		self.slider.valueChanged.connect(self.on_value_changed)

	def value(self):
		return self.slider.value()

	def set_value(self, value):
		current_value = self.slider.value()
		self.slider.setValue(value)

	def set_enabled(self, enabled):
		self.slider.setEnabled(enabled)

	def max(self):
		return self.slider.maximum()

	def min(self):
		return self.slider.minimum()

	def set_max(self, value):
		self.slider.setMaximum(value)

	def set_min(self, value):
		self.slider.setMinimum(value)

	def set_range(self, min_value, max_value):
		self.slider.setRange(min_value, max_value)

	def set_on_value_changed(self, on_changed):
		self._on_changed = SmartCallable.bind_if_func(on_changed, self) if on_changed is not None else None

	def on_value_changed(self, value):
		_value = self._on_changed(value) if self._on_changed else None
		if _value is None:
			_value = value
		self._update_value_label(_value)

	def _update_value_label(self, value):
		self.value_label.setText(str(value))


class NegativeInfinitySliderMixin:
	def _update_value_label(self, value):
		if value < 0:
			self.value_label.setText("∞")
		else:
			super()._update_value_label(value)


class RangeSliderWidget(WidgetBase(QWidget)):
	def __init__(self, min_value, max_value, default_min_value, default_max_value, on_changed=None, fixed_width=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.on_range_changed = Subscription()
		if on_changed is not None:
			_on_changed = SmartCallable.bind_if_func(on_changed, self)
			self.on_range_changed.subscribe(_on_changed)
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		layout = QHBoxLayout()
		self.setLayout(layout)
		range_label_left = QLabel(str(default_min_value))
		layout.addWidget(range_label_left)
		self.range_label_left = range_label_left
		slider_left = QSlider(Qt.Horizontal)
		slider_left.setMinimum(min_value)
		slider_left.setMaximum(max_value)
		slider_left.setValue(default_min_value)
		slider_left.valueChanged.connect(self._on_slider_value_changed)
		layout.addWidget(slider_left)
		self.slider_left = slider_left

		slider_right = QSlider(Qt.Horizontal)
		slider_right.setMinimum(min_value)
		slider_right.setMaximum(max_value)
		slider_right.setValue(default_max_value)
		slider_right.valueChanged.connect(self._on_slider_value_changed)
		layout.addWidget(slider_right)
		self.slider_right = slider_right
		range_label_right = QLabel(str(default_max_value))
		layout.addWidget(range_label_right)
		self.range_label_right = range_label_right

	def set_range(self, *args):
		if len(args) == 1:
			if isinstance(args[0], Range):
				min, max = args[0].min, args[0].max
			elif isinstance(args[0], tuple) or isinstance(args[0], list):
				min, max = args[0]
			else:
				raise ValueError(utils.method.msg("Invalid argument type"))
		elif len(args) == 2:
			min, max = args
		else:
			raise ValueError(utils.method.msg("Invalid number of arguments"))
		self.slider_left.setRange(min, max)
		self.slider_right.setRange(min, max)
		if self.slider_left.value() > self.slider_right.value():
			self.slider_left.setValue(self.slider_right.value())

	def range(self):
		return Range(self.slider_left.value(), self.slider_right.value())

	def set_minimum_width(self, width):
		half_width = width // 2
		self.slider_left.setMinimumWidth(half_width)
		self.slider_right.setMinimumWidth(half_width)


	def set_enabled(self, enabled):
		self.slider_left.setEnabled(enabled)
		self.slider_right.setEnabled(enabled)

	def _on_slider_value_changed(self, value):
		# Disconnect signal handlers temporarily to avoid recursive calls and to make only one slider to trigger the change
		self.slider_left.valueChanged.disconnect()
		self.slider_right.valueChanged.disconnect()
		left_value = self.slider_left.value()
		right_value = self.slider_right.value()
		if left_value > right_value:
			slider_to_update = self.slider_left if value == right_value else self.slider_right
			slider_to_update.setValue(value)
			right_value = left_value = value
		self.range_label_left.setText(str(left_value))
		self.range_label_right.setText(str(right_value))
		self.on_range_changed.notify(left_value, right_value)
		# Reconnect signal handlers
		self.slider_left.valueChanged.connect(self._on_slider_value_changed)
		self.slider_right.valueChanged.connect(self._on_slider_value_changed)


class PairWidget(WidgetBase(AbstractWidget, QWidget)):
	def __init__(self, left, right, fixed_width=None, right_fixed_width=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
		layout = QHBoxLayout()
		self.setLayout(layout)
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		# Left widget
		left_widget = QLabel(left) if isinstance(left, str) else left
		layout.addWidget(left_widget)
		self.left_widget = left_widget
		# Right widget
		right_widget = QLabel(right) if isinstance(right, str) else right
		if right_fixed_width is not None:
			right_widget.setFixedWidth(right_fixed_width)
		layout.addWidget(right_widget)
		self.right_widget = right_widget


class RangeSliderInputWidget(PairWidget):
	def __init__(self, label, min_value, max_value, default_min_value, default_max_value, on_changed, fixed_width=None, *args, **kwargs):
		slider = RangeSliderWidget(min_value, max_value, default_min_value, default_max_value, on_changed)
		self.slider = slider
		super().__init__(label, slider, *args, **kwargs)


class LineInputWidget(PairWidget):
	def __init__(self, label, default_value, on_changed, *args, **kwargs):
		line_edit = QLineEdit()
		super().__init__(label, line_edit, *args, **kwargs)
		self._on_changed = SmartCallable.bind_if_func(on_changed, self) if on_changed is not None else None
		if default_value is not None:
			t = type(default_value)
			assert t is str or t is int or t is float or t is bool
			self.line_edit.setText(str(default_value))
		self.line_edit.textChanged.connect(self.on_text_changed)

	@property
	def line_edit(self):
		return self.right_widget

	def set_value(self, value):
		self.line_edit.setText(str(value))

	def set_enabled(self, enabled):
		self.line_edit.setEnabled(enabled)

	def on_text_changed(self, text):
		_value = self._on_changed(text) if self._on_changed else None
		if _value is None:
			_value = text
		self.line_edit.setText(str(_value))


class CheckboxWidget(WidgetBase(QWidget)):
	def __init__(self, label, default_value, on_changed, fixed_width=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._on_changed = SmartCallable.bind_if_func(on_changed, self) if on_changed is not None else None
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		layout = QHBoxLayout()
		self.setLayout(layout)
		self.checkbox = QCheckBox(label)
		self.checkbox.setChecked(default_value)
		layout.addWidget(self.checkbox)
		self.checkbox.stateChanged.connect(self.on_state_changed)

	def set_value(self, value):
		self.checkbox.setChecked(value)

	def set_enabled(self, enabled):
		self.checkbox.setEnabled(enabled)

	def set_text(self, text):
		self.checkbox.setText(text)

	def on_state_changed(self, state):
		_value = self._on_changed(state == Qt.Checked.value) if self._on_changed else None
		if _value is None:
			_value = state == Qt.Checked.value
		self.checkbox.setChecked(_value)


class TextSpinner(AbstractTextSpinner, QLabel, metaclass=CombinedMetaQtABC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setAlignment(Qt.AlignCenter)

	@AbstractTextSpinner.text.getter
	def text(self):
		return self.text()

	@AbstractTextSpinner.text.setter
	def text(self, value):
		self.setText(value)

# Mixins
class CopyableMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._text = None

	def create_context_menu(self):
		context_menu = QMenu(self)
		copy_action = QAction("Copy", self)
		context_menu.addAction(copy_action)
		copy_action.triggered.connect(self.copy_text)
		# copy_action.triggered.connect(partial(self.copy_text, "some argument"))
		return context_menu

	def text_to_copy(self, context_menu_event):
		pass

	def contextMenuEvent(self, event):
		text = self.text_to_copy(event)
		if text is None:
			return
		self._text = text
		context_menu = self.create_context_menu()
		context_menu.exec(event.globalPos())

	def copy_text(self):
		clipboard = QApplication.clipboard()
		clipboard.setText(self._text)
		self._text = None


class CopyableLabelMixin(CopyableMixin):
	def text_to_copy(self, context_menu_event):
		return self.text()


class CopyableLabel(WidgetBase(CopyableLabelMixin, QLabel)):
	def __init__(self, text="", *args, **kwargs):
		super().__init__(text, *args, **kwargs)
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


class ValueWidget(PairWidget):
	def __init__(self, label, value, *args, **kwargs):
		value_label = CopyableLabel(str(value))
		super().__init__(label, value_label, *args, **kwargs)

	@property
	def value_label(self):
		return self.right_widget

	def set_value(self, value):
		self.right_widget.setText(str(value))

	def set_title(self, title):
		self.left_widget.setText(title)

	def value(self):
		return self.right_widget.text()


class CustomAdjustSizeMixin(AbstractWidget):
	def adjust_size(self):
		geometry = self._adjusted_geometry()
		size = geometry.size()
		self.setFixedSize(size)
		self.setGeometry(geometry)
		# self._on_resized(size)

	def _adjusted_geometry(self):
		return self.geometry()


class FitContentsMixin(CustomAdjustSizeMixin):
	def _on_contents_changed(self):
		super()._on_contents_changed()
		for child in self.children():
			if isinstance(child, AbstractWidget):
				child.adjust_size()
			elif isinstance(child, QWidget):
				child.adjustSize()

	def _adjusted_geometry(self):
		geometry = super()._adjusted_geometry()
		new_size = self.calculate_size()
		return QRect(geometry.topLeft(), new_size)

	def _on_child_added(self, child):
		self._on_contents_changed()

	def _on_child_removed(self, child):
		self._on_contents_changed()

	def calculate_size(self):
		# Iterate over all children and calculate the bounding rect
		geometry = utils.pyside.children_geometry(self)
		return geometry.size()


class ExpandableWidget(WidgetBase(AbstractWidget, QWidget)): # TODO: Inherit from FitContentsMixin
	on_collapsed = Signal()
	on_expanded = Signal()
	on_state_changed = Signal(bool)

	def __init__(self, title=None, expanded_widget=None, collapsed_widget=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Layouting
		layout = QVBoxLayout()
		self.setLayout(layout)
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
		if self.is_expanded():
			return False
		self.expand_button.setText("-")
		self.expand_button.clicked.disconnect()
		self.expand_button.clicked.connect(self._on_collapse_click)
		if self.expanded_widget is not None:
			self.expanded_widget.show()
			self._on_contents_changed()
		self.on_expanded.emit()
		self.on_state_changed.emit(True)
		log.debug(utils.method.msg_kw())
		return True

	def collapse(self):
		if not self.is_expanded():
			return False
		self.expand_button.setText("+")
		self.expand_button.clicked.disconnect()
		self.expand_button.clicked.connect(self._on_expand_click)
		if self.expanded_widget is not None:
			self.expanded_widget.hide()
			self._on_contents_changed()
		self.on_collapsed.emit()
		self.on_state_changed.emit(False)
		log.debug(utils.method.msg_kw())
		return True

	def set_expanded(self, expanded):
		if expanded:
			self.expand()
		else:
			self.collapse()

	def is_expanded(self):
		expanded_widget = self.expanded_widget
		return expanded_widget is not None and not expanded_widget.isHidden()


class DeallocateExpandedWidgetMixin(ABCQt):
	@abstractmethod
	def create_expanded_widget(self):
		pass

	def expand(self):
		if self.is_expanded():
			return False
		assert self.expanded_widget is None
		self.expanded_widget = self.create_expanded_widget()
		self.expanded_widget.hide()
		return super().expand()

	def collapse(self):
		if not super().collapse():
			return False
		if self.expanded_widget is not None:
			self.expanded_widget.setParent(None)
			self.expanded_widget.deleteLater()
			self.expanded_widget = None
		return True


class ResizeEventFilter(QObject):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.target_widget = None
		self.callback = None

	def set_target(self, target_widget, callback):
		self.target_widget = target_widget
		self.callback = callback
		target_widget.installEventFilter(self)

	def eventFilter(self, obj, event):
		if obj == self.target_widget and event.type() == QEvent.Resize:
			if self.callback:
				self.callback(obj, event)
		return super().eventFilter(obj, event)


class ClampGeometryMixin(CustomAdjustSizeMixin):
	def __init__(self, *args, clamper_widget=None, **kwargs):
		self._clamper_widget = clamper_widget
		super().__init__(*args, **kwargs)
		# Subscribe on resize event of the clamper widget
		if clamper_widget:
			self.resize_event_filter = ResizeEventFilter(self)
			self.resize_event_filter.set_target(clamper_widget, self._on_clamper_resized)

	def _adjusted_geometry(self):
		geometry = super()._adjusted_geometry()
		clamped_geometry = self.clamped_geometry(geometry)
		return clamped_geometry or geometry

	def clamped_geometry(self, geometry):
		if self._clamper_widget:
			intersection = utils.pyside.clamp_geometry(self, self._clamper_widget, geometry)
			return intersection
		return None
	
	def _on_clamper_resized(self, obj, event):
		self.adjust_size()

class FitContentsListMixin(FitContentsMixin):
	def calculate_size(self):
		total_width = max(self.sizeHintForColumn(0) + self.verticalScrollBar().sizeHint().width(), self.width())
		total_height = self.sizeHintForRow(0) * self.count() + self.horizontalScrollBar().sizeHint().height()
		return QSize(total_width, total_height)


class FitContentsTableMixin(FitContentsMixin):
	def calculate_size(self):
		vertical_scrollbar_width = self.verticalScrollBar().sizeHint().width()
		horizontal_scrollbar_height = self.horizontalScrollBar().sizeHint().height()
		header_height = self.horizontalHeader().sizeHint().height()
		left_header_width = self.verticalHeader().sizeHint().width()
		total_width = sum(self.columnWidth(i) for i in range(self.columnCount())) + vertical_scrollbar_width + left_header_width
		total_height = sum(self.rowHeight(i) for i in range(self.rowCount())) + horizontal_scrollbar_height + header_height
		return QSize(total_width, total_height)


class CopyableListElementMixin(CopyableMixin):
	def text_to_copy(self, context_menu_event):
		item = self.itemAt(context_menu_event.pos())
		return item.text() if item else None


class DataTableMixin(ABCQt):
	column_titles: OrderedDict = None
	def __init__(self, data=None, excluded_columns=None, *args, **kwargs):
		self._data_list = None
		super().__init__(*args, **kwargs)
		verify(self.column_titles is not None, utils.method.msg("Column_titles must be defined"))
		self.columns = self.column_titles.copy()
		if excluded_columns is not None:
			self.columns = utils.collection.exclude(self.column_titles, excluded_columns)
		self.update(0, data)

	def gen_table_values(self, data_list):
		rows = []
		for data in data_list:
			values = []
			for col in self.columns.keys():
				value = self.column_value(data, col)
				values.append(value)
			rows.append(values)
		return rows

	@abstractmethod
	def column_value(self, data, column):
		pass

	def _on_data_list_changed(self, previous_data_list: WeakList):
		pass

	def update(self, dt=None, data=None, force=False):
		if not force:
			if data is None:
				return
			if self._data_list == data:
				return
			else:
				previous_data_list = self._data_list
				self._data_list = WeakList(data)
				self._on_data_list_changed(previous_data_list)
				# Clear the table
				self.clear(call_contents_changed=False)
				# Add columns
				for title in self.columns.values():
					self.add_column(title)
		else:
			self.clear_contents(call_contents_changed=False)
		# Fill the rows
		items = self.gen_table_values(data or self._data_list)
		self.add_items(items)
		super().update(dt)


class AbstractListWidget(AbstractWidget):
	@abstractmethod
	def _add_item(self, *args, **kwargs):
		pass

	def add_items(self, items):
		for item in items:
			self._add_item(item)
		self._on_contents_changed()

	def add_item(self, *args, **kwargs):
		self._add_item(*args, **kwargs)
		self._on_item_added()
		self._on_contents_changed()

	def _on_item_added(self):
		pass


# Mixins logic executed in the order opposite to the inheritance order
class ListWidget(WidgetBase(ClampGeometryMixin, FitContentsListMixin, CopyableListElementMixin, AbstractListWidget, QListWidget)):
	def _add_item(self, item):
		if isinstance(item, QWidget):
			_item = QListWidgetItem(self)
			def on_item_resized(widget, size, _item=_item):
				_item.setSizeHint(size)
			item.on_resized.connect(on_item_resized)
			on_item_resized(item, item.geometry().size())
			self.setItemWidget(_item, item)
			return _item
		else:
			self.addItem(item)
			return item

class TableWidget(WidgetBase(ClampGeometryMixin, FitContentsTableMixin, CopyableListElementMixin, AbstractListWidget, QTableWidget)):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setColumnCount(0)
		self.horizontalHeader().setSectionsClickable(True)
		self.horizontalHeader().sectionClicked.connect(self.sort_by_column)
		self._on_contents_changed()

	def clear(self, call_contents_changed=True):
		super().clear()
		self.setRowCount(0)
		self.setColumnCount(0)
		if call_contents_changed:
			self._on_contents_changed()

	def clear_contents(self, call_contents_changed=True):
		self.setRowCount(0)

	def add_column(self, column_name):
		self.insertColumn(self.columnCount())
		header_item = QTableWidgetItem(column_name)
		self.setHorizontalHeaderItem(self.columnCount() - 1, header_item)
		self._on_contents_changed()

	def _add_item(self, column_values):
		row_position = self.rowCount()
		self.insertRow(row_position)
		for column, value in enumerate(column_values):
			if isinstance(value, QWidget):
				verify(isinstance(value, AbstractWidget), ValueError("Please use AbstractWidget or its subclasses for the table widget items to be able to subscribe to on_resized signal"))
				self.setCellWidget(row_position, column, value)
				# Adapt the row height to the widget height
				attr_name = f"on_cell_resized_{row_position}_{column}"
				def on_cell_resized(self, widget, size, row_position=row_position, column=column):
					row_height = self.rowHeight(row_position)
					column_width = self.columnWidth(column)
					self.setRowHeight(row_position, max(size.height(), row_height))
					self.setColumnWidth(column, max(size.width(), column_width))
				# TODO: check if cleaning upon the widget deletion is needed
				method = types.MethodType(on_cell_resized, self)
				setattr(self, attr_name, method)
				method = getattr(self, attr_name)
				value.on_resized.connect(method)
			else:
				table_item = QTableWidgetItem(str(value) if value is not None else '')
				self.setItem(row_position, column, table_item)

	def sort_by_column(self, column_index):
		order = self.horizontalHeader().sortIndicatorOrder()
		self.sortItems(column_index, order)

	def _on_contents_changed(self):
		self.resizeColumnsToContents()
		super()._on_contents_changed()
			
class SectionWidget(WidgetBase(AbstractWidget, QWidget)):
	def __init__(self, title=None, title_style=None, layout_cls=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		_layout_cls = layout_cls or QVBoxLayout
		layout = _layout_cls()
		self._layout = layout
		self.title_label = None
		if title is not None:
			root_layout = QVBoxLayout()
			self.setLayout(root_layout)
			title_label = QLabel(title)
			_title_style = title_style or "font: 12pt Arial; font-weight: bold;"
			title_label.setStyleSheet(_title_style)
			title_label.setAlignment(Qt.AlignCenter)
			root_layout.addWidget(title_label)
			self.title_label = title_label
			root_layout.addLayout(layout)
		else:
			self.setLayout(layout)

	def layout(self):
		return self._layout

class SpinnerDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Processing...")
		self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
		
		layout = QVBoxLayout()
		self.label = QLabel("Loading...")
		self.spinner = TextSpinner()

		layout.addWidget(self.label)
		layout.addWidget(self.spinner)
		self.setLayout(layout)

		# Update spinner text periodically to simulate spinning
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_spinner)
		self.timer.start(100)  # Adjust the interval as needed

	def update_spinner(self):
		current_text = self.spinner.text()
		new_text = current_text[-1] + current_text[:-1]  # Simple text rotation
		self.spinner.setText(new_text)

	def closeEvent(self, event):
		self.timer.stop()
		super().closeEvent(event)


class ExpandableDataWidget(DeallocateExpandedWidgetMixin, ExpandableWidget):
	def __init__(self, data=None, excluded_columns=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data_list = None
		self._excluded_columns = excluded_columns
		self.update(data=data)

	def on_data_widget_resized(self, obj, size):
		self._on_contents_changed()
	
	def on_data_widget_parent_changed(self, obj):
		self._on_contents_changed()

	def expand(self):
		if not super().expand():
			return False
		self.expanded_widget.on_resized.connect(self.on_data_widget_resized)
		self.expanded_widget.on_parent_changed.connect(self.on_data_widget_parent_changed)
		# def on_item_widget_resized(obj, size):
		# 	widget.adjust_size()
		# item.on_resized.connect(on_item_widget_resized)
		# self.expanded_widget.show() # TODO: Needed?
		return True

	def update(self, data=None, *args, **kwargs):
		if data is not None:
			if data != self._data_list:
				self._data_list = WeakList(data)
		self.collapsed_widget.update(data)
		if self.expanded_widget is not None:
			self.expanded_widget.update(data=data)
		super().update(*args, **kwargs)

	class CollapsedWidget(ValueWidget):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
		
		def update(self, data=None, *args, **kwargs):
			if data is not None:
				count = len(data)
				self.set_value(count)
			super().update(*args, **kwargs)


class DataWidgetMixin:
	def __init__(self, *args, **kwargs): # Carries-over all the arguments to update() method
		update_args, other_args, other_kwargs = self._update_signature_args(*args, **kwargs)
		super().__init__(*other_args, **other_kwargs)
		self.update(*args, **kwargs)

	# NoValue is used for required parameters, but allows to other classes update method to be called
	def _update_signature_args(self, data=None, *args, **kwargs):
		return (data), args, kwargs

	def update(self, *args, **kwargs):
		update_args, other_args, other_kwargs = self._update_signature_args(*args, **kwargs)
		data = update_args
		if data is NoValue: # Allow other classes update methods to be called, but parameterized only with kwargs
			return super().update(*args, **kwargs)


class SceneItemsMixin:
	def update_line_item(self, scene, name, line: QLineF, pen=None):
		item = self.item(scene, name, QGraphicsLineItem)
		item.setLine(line)
		if pen is not None:
			item.setPen(pen)
		return item
	
	def item(self, name, cls, *args, scene=None, **kwargs):
		item = getattr(self, name, None)
		if item is None:
			item = cls(*args, **kwargs)
			if scene is not None:
				scene.addItem(item)
			else:
				item.setParentItem(self)
			setattr(self, name, item)
		return item

	def remove_item(self, name):
		item = getattr(self, name, None)
		if item is not None:
			scene = item.scene()
			if scene is not None:
				scene.removeItem(item)
			item.setParentItem(None)
			setattr(self, name, None)
			return True
		return False

	def item_in_list(self, scene, list_name, index, cls, *args, **kwargs):
		lst = getattr(self, list_name, None)
		if lst is None:
			lst = []
			item = cls(*args, **kwargs)
			scene.addItem(item)
		item = lst[index] if index < len(lst) else None
		if item is None:
			item = cls(*args, **kwargs)
			scene.addItem(item)
			lst.append(item)
		return item, index

	def remove_items_in_list(self, list_name):
		lst = getattr(self, list_name, None)
		if lst is not None:
			for item in lst:
				scene = item.scene()
				scene.removeItem(item)
				item.setParentItem(None)
			setattr(self, list_name, None)
			return True
		return False
