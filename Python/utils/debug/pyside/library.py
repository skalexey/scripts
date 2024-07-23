from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget

from utils.log.logger import Logger

log = Logger()

def inspect_widgets(widget, level=0, attrs=None):
	"""Recursively print all widgets in the hierarchy."""
	if isinstance(widget, QWidget):
		_default_attrs = {"isVisible", "isEnabled", "text"}
	elif isinstance(widget, QLayout):
		_default_attrs = {"spacing"}
	elif isinstance(widget, QLayoutItem):
		_default_attrs = set()
	else:
		return
	_default_attrs.update({"geometry", "sizeHint", "sizePolicy"})
	_attrs = attrs.copy() if attrs is not None else _default_attrs
	def add_attr(obj, attr_name):
		if attr_name in _attrs:
			_attrs.remove(attr_name)
			attr = getattr(obj, attr_name, None)
			if attr is not None:
				val = attr() if callable(attr) else attr
				if isinstance(val, str):
					return f" {attr_name}='{val}'"
				else:
					return f" {attr_name}={val}"
		return ""

	def add_attrs(obj, *attrs):
		return "".join(add_attr(obj, attr) for attr in attrs)
	
	msg = ""
	msg = add_attrs(widget, *_attrs) + msg
	log.debug(f"{'  ' * level} widget={widget}{msg}")
	if isinstance(widget, QLayout):
		for i in range(widget.count()):
			item = widget.itemAt(i)
			inspect_widgets(item, level + 1, attrs)
	elif isinstance(widget, QLayoutItem):
		inspect_widgets(widget.widget() or widget.layout(), level + 1, attrs)
	elif isinstance(widget, QWidget):
		for child in widget.children():
			inspect_widgets(child, level + 1, attrs)
