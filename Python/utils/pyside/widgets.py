from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QClipboard
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from utils.memory import SmartCallable
from utils.pyside import WidgetBase
from utils.text import AbstractTextSpinner


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


class ExpandableWidget(WidgetBase(QWidget)):
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

	def collapse(self):
		self.expand_button.setText("+")
		self.expand_button.clicked.disconnect()
		self.expand_button.clicked.connect(self._on_expand_click)
		if self.expanded_widget is not None:
			self.expanded_widget.hide()


class ResizableListMixin:
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


class CopyableListElementMixin(CopyableMixin):
	def text_to_copy(self, context_menu_event):
		item = self.itemAt(context_menu_event.pos())
		return item.text() if item else None


class ListWidget(WidgetBase(ResizableListMixin, CopyableListElementMixin, QListWidget)):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.adjustSize()