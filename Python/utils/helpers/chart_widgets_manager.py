from abc import ABC, abstractmethod

from utils.helpers.data_widgets_update import DataWidgetsUpdateMixin


class ChartWidgetsManager(DataWidgetsUpdateMixin, ABC):
	def __init__(self, app_context, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.app_context = app_context

	# DataWidgetsUpdateMixin overrides
	def _add_widget(self, data):
		widget = super()._add_widget(data)
		if widget is not None:
			chart = self.app_context.main_window.chart_view
			chart.scene.addItem(widget)
		return widget

	def _destroy_widget(self, widget):
		chart = self.app_context.main_window.chart_view
		chart.scene.removeItem(widget)
