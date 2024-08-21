import weakref
from abc import ABC, abstractmethod

from utils.helpers.data_widgets_update import DataWidgetsUpdateMixin


class ChartWidgetsManager(DataWidgetsUpdateMixin, ABC):
	def __init__(self, app_context, *args, parent=None, **kwargs):
		self.set_parent_widget(parent)
		super().__init__(*args, **kwargs)
		self.app_context = app_context

	# DataWidgetsUpdateMixin overrides
	def _add_widget(self, data, *args, **kwargs):
		widget = super()._add_widget(data, *args, **kwargs)
		if widget is not None:
			parent = self.parent_widget
			if parent is not None:
				widget.setParentItem(parent)
			else:
				chart = self.app_context.main_window.chart_view
				chart.scene.addItem(widget)
		return widget

	def _destroy_widget(self, widget):
		scene = widget.scene()
		scene.removeItem(widget)
		widget.setParentItem(None)

	@property
	def parent_widget(self):
		return self._parent_widget_ref() if self._parent_widget_ref is not None else None

	def set_parent_widget(self, parent_widget):
		self._parent_widget_ref = weakref.ref(parent_widget) if parent_widget is not None else None
