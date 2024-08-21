import weakref
from abc import ABC, abstractmethod

from utils.collection.ordered_dict import OrderedDict
from utils.collection.weak_list import WeakList


class DataWidgetsUpdateMixin(ABC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data_list = WeakList() # WeakList(on_destroyed=self._on_data_destroyed)
		self._widgets = OrderedDict()
		self._data_indexes = {}
		self._data_ids = {}

	def _on_data_destroyed(self, data_id, index):
		stored_index = self._data_indexes.pop(data_id)
		assert index == stored_index
		self._data_ids.pop(stored_index)
		self._data_list.pop(index)
		widget_ref = self._widgets.pop(data_id)
		widget = widget_ref()
		self._destroy_widget(widget)

	def get_widget(self, data):
		data_id = self._get_data_id(data)
		widget_ref = self._widgets.get(data_id)
		return widget_ref()

	def clear(self):
		for widget, data in self.pairs():
			self._destroy_widget(widget)
		self._data_list.clear()
		self._widgets.clear()
		self._data_indexes.clear()
		self._data_ids.clear()

	@abstractmethod
	def _destroy_widget(self, widget):
		pass
		# Example:
		# chart = self.app_context.main_window.chart_view
		# chart.scene.removeItem(widget)

	@abstractmethod
	def _create_widget(self, data, *args, **kwargs):
		pass
		# Example:
		# return TargetWidget(data)

	def _add_widget(self, data, *args, **kwargs):
		widget = self._create_widget(data, *args, **kwargs)
		if widget is not None:
			data_id = self._get_data_id(data)
			assert data_id not in self._widgets
			self._widgets[data_id] = weakref.ref(widget) # TODO: add finalizer and remove the data and widget entries?
		return widget

	def _get_data_id(self, data):
		return id(data) # Default implementation
		# Override example:
		# return data.id

	def pairs(self):
		# Data can be destroyed and the widget can still be in the list, that is the chance to clear or destroy the widget for a user.
		return ((widget_ref(), self._data_list[index]) for data_id, index in self._data_indexes.items() if (widget_ref := self._widgets.get(data_id)) is not None)

	# If data_list is None, it will update all the widgets with the current data list. Can be used as a "force" update.
	def update(self, data_list=None, *args, **kwargs):
		assert len(self._widgets) == len(self._data_list)
		if data_list is None: # Just update with the current data
			for widget, data in self.pairs():
				widget.update(data, *args, **kwargs)
		else: # Update with the new data list
			data_size = len(data_list)
			stored_size = len(self._data_list)
			list_updated = False
			# Remove no longer needed widgets
			to_remove_count = stored_size - data_size
			for i in range(to_remove_count):
				data = self._data_list.pop()
				# Data can be destroyed, so data_id is taken from _data_ids
				index = stored_size - i - 1
				data_id = self._data_ids.pop(index)
				stored_index = self._data_indexes.pop(data_id)
				assert index == stored_index
				widget_ref = self._widgets.pop(data_id)
				widget = widget_ref()
				self._destroy_widget(widget)
			# Update existing widgets
			stored_size = len(self._data_list)
			if self._update_widgets(data_list, *args, **kwargs):
				list_updated = True
			assert len(self._widgets) == len(self._data_list)
			# Add new widgets
			to_add_count = data_size - stored_size
			for i in range(to_add_count):
				data = data_list[stored_size + i]
				self._add_widget(data, *args, **kwargs)
				self._data_list.append(data)
				data_id = self._get_data_id(data)
				assert data_id not in self._data_indexes
				self._data_indexes[data_id] = stored_size + i
				self._data_ids[stored_size + i] = data_id
			list_updated = list_updated or to_add_count > 0 or to_remove_count > 0
			assert len(self._widgets) == len(self._data_list)

	def _update_widgets(self, data_list, *args, **kwargs):
		assert len(self._widgets) == len(self._data_list)
		if data_list == self._data_list:
			return False
		widgets = []
		widget_count = len(self._widgets)
		data_count = len(self._data_list)
		assert widget_count == data_count
		for widget, data in self.pairs():
			widgets.append(widget)
		assert len(widgets) == widget_count
		self._widgets.clear()
		self._data_list.clear()
		self._data_indexes.clear()
		self._data_ids.clear()
		assert len(widgets) == widget_count
		assert widget_count == data_count
		for i, widget in enumerate(widgets):
			data = data_list[i]
			if widget:
				widget.update(data, *args, **kwargs)
			self._data_list.append(data)
			data_id = self._get_data_id(data)
			self._data_indexes[data_id] = i
			self._data_ids[i] = data_id
			self._widgets[data_id] = weakref.ref(widget)
		assert len(self._widgets) == len(self._data_list)
		assert widget_count == data_count
		assert widget_count == len(self._widgets)
		return True
