import weakref
from abc import ABC, abstractmethod

from utils.collection.ordered_dict import OrderedDict
from utils.collection.weak_list import WeakList


class DataWidgetsUpdateMixin(ABC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data_list = WeakList()
		self._widgets = OrderedDict()

	@abstractmethod
	def _destroy_widget(self, widget):
		pass
		# Example:
		# chart = self.app_context.main_window.chart_view
		# chart.scene.removeItem(widget)

	@abstractmethod
	def _create_widget(self, data):
		pass
		# Example:
		# return TargetWidget(data)

	def _add_widget(self, data):
		widget = self._create_widget(data)
		if widget is not None:
			chart = self.app_context.main_window.chart_view
			chart.scene.addItem(widget)
			data_id = self._get_data_id(data)
			self._widgets[data_id] = weakref.ref(widget)
		return widget

	def _get_data_id(self, data):
		return id(data) # Default implementation
		# Override example:
		# return data.id

	def update(self, data_list):
		if data_list is not None:
			if data_list != self._data_list:
				self._data_list = WeakList(data_list)
				for widget in filter(None, (ref() for ref in self._widgets.values())): 
					self._destroy_widget(widget)
				self._widgets.clear()
				for data in data_list:
					self._add_widget(data)

	def _update_widget(self, data):
		id = self._get_data_id(data)
		ref = self._widgets.get(id)
		if not ref:
			return
		widget = ref()
		if widget:
			widget.update(data)