from abc import ABC, abstractmethod

from PySide6.QtCore import QEvent, QObject, QRect, QSize, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import utils.class_utils as class_utils
import utils.lang
import utils.method
import utils.pyside
from utils.log.logger import Logger
from utils.memory import SmartCallable
from utils.pyside import WidgetBase
from utils.text import AbstractTextSpinner

log = Logger()

# Use EnforcedABCMeta instead of ABCMeta since QtWidget metaclass suppresses the abstractmethod checking behavior
class CombinedMetaQtABC(class_utils.EnforcedABCMeta, type(QWidget)):
	pass


class ABCQt(ABC, metaclass=CombinedMetaQtABC):
	pass


class AbstractWidget(ABCQt):
	on_resized = Signal(QWidget)
	on_parent_changed = Signal(QWidget)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._on_contents_changed()

	def _adjust_size(self):
		self.adjustSize()
		self._on_resized()

	def _on_resized(self):
		self.on_resized.emit(self)

	def _on_contents_changed(self):
		self._adjust_size()

	def update(self, dt, *args, **kwargs):
		pass
		# self._on_contents_changed() # TODO: consider lighter options
		# super().update(*args, **kwargs)

	def event(self, event):
		if event.type() == QEvent.ParentChange:
			self.on_parent_changed.emit(self)
		return super().event(event)


class SliderInputWidget(WidgetBase(QWidget)):
	def __init__(self, label, min_value, max_value, default_value, on_changed, slider_fixed_width=None, value_label_fixed_width=None, fixed_width=None, parent=None, parent_layout=None, *args, **kwargs):
		super().__init__(parent=parent, parent_layout=parent_layout, *args, **kwargs)
		self._on_changed = SmartCallable.bind_if_func(on_changed, self) if on_changed is not None else None
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		layout = QHBoxLayout()
		self.setLayout(layout)
		label_widget = QLabel(label)
		layout.addWidget(label_widget)
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

	def on_value_changed(self, value):
		_value = self._on_changed(value) if self._on_changed else None
		if _value is None:
			_value = value
		self.value_label.setText(str(_value))


class LineInputWidget(WidgetBase(QWidget)):
	def __init__(self, label, default_value, on_changed, input_fixed_width=None, fixed_width=None, parent=None, parent_layout=None, *args, **kwargs):
		super().__init__(parent=parent, parent_layout=parent_layout, *args, **kwargs)
		self._on_changed = SmartCallable.bind_if_func(on_changed, self) if on_changed is not None else None
		if fixed_width is not None:
			self.setFixedWidth(fixed_width)
		layout = QHBoxLayout()
		self.setLayout(layout)
		label_widget = QLabel(label)
		layout.addWidget(label_widget)
		self.line_edit = QLineEdit()
		if default_value is not None:
			t = type(default_value)
			assert t is str or t is int or t is float or t is bool
			self.line_edit.setText(str(default_value))
		if input_fixed_width is not None:
			self.line_edit.setFixedWidth(input_fixed_width)
		layout.addWidget(self.line_edit)
		self.line_edit.textChanged.connect(self.on_text_changed)

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
	def __init__(self, label, default_value, on_changed, fixed_width=None, parent=None, parent_layout=None, *args, **kwargs):
		super().__init__(parent=parent, parent_layout=parent_layout, *args, **kwargs)
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


class ExpandableWidget(WidgetBase(AbstractWidget, QWidget)):
	def __init__(self, title=None, expanded_widget=None, collapsed_widget=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Layouting
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		self.hlayout = QHBoxLayout()
		self.hlayout.setAlignment(Qt.AlignLeft)
		self.layout.addLayout(self.hlayout)
		# Widgets
		self.collapsed_widget = collapsed_widget or QLabel(title or "")
		self.hlayout.addWidget(self.collapsed_widget)
		self.expanded_widget = expanded_widget
		if self.expanded_widget is not None:
			self.layout.addWidget(self.expanded_widget)
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
		log.debug(utils.method.msg_kw())

	def collapse(self):
		self.expand_button.setText("+")
		self.expand_button.clicked.disconnect()
		self.expand_button.clicked.connect(self._on_expand_click)
		if self.expanded_widget is not None:
			self.expanded_widget.hide()
		log.debug(utils.method.msg_kw())


class DeallocateExpandedWidgetMixin(ABCQt):
	@abstractmethod
	def create_expanded_widget(self):
		pass

	def expand(self):
		super().expand()
		self.expanded_widget = self.create_expanded_widget()

	def collapse(self):
		if self.expanded_widget is not None:
			self.expanded_widget.setParent(None)
			self.expanded_widget.deleteLater()
			self.expanded_widget = None
		super().collapse()


class CustomAdjustSizeMixin(AbstractWidget):
	def _adjust_size(self):
		geometry = self._adjusted_geometry()
		self.setFixedSize(geometry.size())
		self.setGeometry(geometry)
		self._on_resized()

	def _adjusted_geometry(self):
		return self.geometry()


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
		self._adjust_size()

class FitContentsMixin(CustomAdjustSizeMixin):
	def _adjusted_geometry(self):
		geometry = super()._adjusted_geometry()
		new_size = self.calculate_size()
		return QRect(geometry.topLeft(), new_size)

	def calculate_size(self):
		raise NotImplementedError("Subclasses should implement this method.")
	

class FitContentsListMixin(FitContentsMixin):
	def calculate_size(self):
		total_width = max(self.sizeHintForColumn(0) + self.verticalScrollBar().sizeHint().width(), self.width())
		total_height = self.sizeHintForRow(0) * self.count() + self.horizontalScrollBar().sizeHint().height()
		return QSize(total_width, total_height)


class FitContentsTableMixin(FitContentsMixin):
	def calculate_size(self):
		total_width = sum(self.columnWidth(i) for i in range(self.columnCount())) + self.verticalScrollBar().sizeHint().width()
		total_height = sum(self.rowHeight(i) for i in range(self.rowCount())) + self.horizontalScrollBar().sizeHint().height()
		return QSize(total_width, total_height)


class CopyableListElementMixin(CopyableMixin):
	def text_to_copy(self, context_menu_event):
		item = self.itemAt(context_menu_event.pos())
		return item.text() if item else None


class AbstractListWidget(AbstractWidget):
	@abstractmethod
	def _add_item(self, *args, **kwargs):
		pass

	def add_items(self, items):
		for item in items:
			self._add_item(*item)
		self._on_contents_changed()

	def add_item(self, *args, **kwargs):
		self._add_item(*args, **kwargs)
		self._on_item_added()
		self._on_contents_changed()

	def _on_item_added(self):
		pass


# Mixins logic executed in the order opposite to the inheritance order
class ListWidget(WidgetBase(ClampGeometryMixin, FitContentsListMixin, CopyableListElementMixin, AbstractListWidget, QListWidget)):
	def _add_item(self, item_text):
		self.addItem(item_text)

class TableWidget(WidgetBase(ClampGeometryMixin, FitContentsTableMixin, CopyableListElementMixin, AbstractListWidget, QTableWidget)):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setColumnCount(0)
		self.horizontalHeader().setSectionsClickable(True)
		self.horizontalHeader().sectionClicked.connect(self.sort_by_column)
		self._on_contents_changed()

	def add_column(self, column_name):
		self.insertColumn(self.columnCount())
		header_item = QTableWidgetItem(column_name)
		self.setHorizontalHeaderItem(self.columnCount() - 1, header_item)
		self.resizeColumnsToContents()

	def _add_item(self, *column_values):
		row_position = self.rowCount()
		self.insertRow(row_position)
		for column, value in enumerate(column_values):
			table_item = QTableWidgetItem(str(value) if value is not None else '')
			self.setItem(row_position, column, table_item)
	
	def sort_by_column(self, column_index):
		order = self.horizontalHeader().sortIndicatorOrder()
		self.sortItems(column_index, order)

	def _on_contents_changed(self):
		self.resizeColumnsToContents()
		super()._on_contents_changed()
