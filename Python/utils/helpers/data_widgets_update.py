from abc import ABC, abstractmethod
from collections import defaultdict

import utils.method
from utils.collection.weak_list import WeakList
from utils.log.logger import Logger
from utils.profile.profiler import TimeProfiler

log = Logger()


class DataWidgetsUpdateMixin(ABC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data_list = WeakList() # WeakList(on_destroyed=self._on_data_destroyed)
		self._widgets = WeakList()
		self._data_indexes = defaultdict(set)
		self._data_ids = []

	def widgets(self):
		return self._widgets

	def pairs(self):
		# Data can be destroyed and the widget can still be in the list, that is the chance to clear or destroy the widget for a user.
		return ((widget, self._data_list[index]) for index, widget in enumerate(self._widgets))
		# return ((widget_ref(), self._data_list[index]) for data_id, index in self._data_indexes.items() if (widget_ref := self._widgets[index]) is not None)

	def _on_widgets_removed(self, count):
		pass

	def _on_data_destroyed(self, data_id, index):
		self._remove_data_id_index(data_id, index)
		self._data_ids.pop(index)
		self._data_list.pop(index)
		widget = self._widgets.pop(index)
		self._destroy_widget(widget)

	def _data_id_indexes(self, data_id):
		indexes = self._data_indexes.get(data_id)
		return indexes if indexes is not None else set()

	def _remove_data_id_index(self, data_id, index):
		stored_indexes = self._data_id_indexes(data_id)
		len_before = len(stored_indexes)
		stored_indexes.remove(index)
		len_after = len(stored_indexes)
		if len(stored_indexes) == 0:
			del self._data_indexes[data_id]
		return len_before > len_after

	def get_widgets_by_data(self, data):
		data_id = self._get_data_id(data)
		indexes = self._data_id_indexes(data_id)
		widgets = [self._widgets[i] for i in indexes]
		return widgets
	
	def get_widget_at(self, index):
		return self._widgets[index]

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
			stored_size = len(self._data_list)
			self._widgets.append(widget) # TODO: add finalizer and remove the data and widget entries?
			self._data_list.append(data)
			data_id = self._get_data_id(data)
			# log.debug(f"	Adding widget: {widget}, data_id: {data_id}, index: {stored_size}")
			assert data_id not in self._data_indexes
			self._data_indexes[data_id].add(stored_size)
			self._data_ids.append(data_id)
		# data_indexes_count_assert = sum(len(indexes) for indexes in self._data_indexes.values())
		# assert len(self._data_ids) == data_indexes_count_assert == len(self._data_list) == len(self._widgets)
		return widget

	def _get_data_id(self, data):
		return id(data) # Default implementation
		# Override example:
		# return data.id

	# If data_list is None, it will update all the widgets with the current data list. Can be used as a "force" update, but with current data.
	def update(self, data_list=None, *args, force=False, **kwargs):
		# profiler = TimeProfiler(print_function=log.verbose)
		# profiler.start()
		assert len(self._widgets) == len(self._data_list)
		if data_list is None: # Just update with the current data
			# profiler.mark("Updating with the current data list")
			for widget, data in self.pairs():
				widget.update(data, *args, **kwargs)
			# profiler.mark(f"Updated {len(self._widgets)} widgets with the current data list")
		else: # Update with the new data list
			# profiler.mark("Updating with the new data list")
			data_size = len(data_list)
			stored_size = len(self._data_list)
			# Remove no longer needed widgets
			to_remove_count = stored_size - data_size
			for i in range(to_remove_count):
				data = self._data_list.pop()
				# Data can be destroyed, so data_id is taken from _data_ids
				data_id = self._data_ids.pop()
				removed = self._remove_data_id_index(data_id, stored_size - i - 1)
				assert removed
				widget = self._widgets.pop()
				self._destroy_widget(widget)
			if to_remove_count > 0:
				# profiler.mark(f"Removed {to_remove_count} widgets")
				self._on_widgets_removed(to_remove_count)
				# profiler.mark("Called on_widgets_removed")
				stored_size = len(self._data_list)
			# Update existing widgets
			# profiler.mark("Calling _update_widgets()")
			self._update_widgets(data_list, *args, force=force, **kwargs)
			# profiler.mark("_update_widgets() called")
			assert len(self._widgets) == len(self._data_list)
			# Add new widgets
			# profiler.mark("calling _add_new_widgets()")
			to_add_count = self._add_new_widgets(data_list, *args, **kwargs)
			# profiler.mark(f"_add_new_widgets() called: Added {to_add_count} new widgets")
			assert len(self._widgets) == len(self._data_list)
			# log.verbose(f'			{utils.method.msg(f"updated {len(data_list)} widgets within {profiler.measure().timespan} seconds")}')
			# profiler.print_marks("  			{description} within {timespan} seconds")

	def _add_new_widgets(self, data_list, *args, **kwargs):
		data_size = len(data_list)
		stored_size = len(self._data_list)
		to_add_count = data_size - stored_size
		for i in range(to_add_count):
			data = data_list[stored_size + i]
			self._add_widget(data, *args, **kwargs)
		return to_add_count

	def _update_widgets(self, data_list, *args, force=False, **kwargs):
		# TODO: check for repeated data (whether it works well or breaks something)
		# profiler = TimeProfiler(print_function=log.verbose)
		# profiler.start()
		# log.verbose(utils.function.msg(f"			Updating {len(data_list)} widgets..."))
		assert len(self._widgets) == len(self._data_list)
		updated_count = 0
		if not force:
			if data_list == self._data_list:
				return updated_count
		# profiler.mark("Compared data lists")
		widgets_to_update = []
		widget_count = len(self._widgets)
		data_count = len(self._data_list)
		assert widget_count == data_count
		# for i, (data_id, widget) in enumerate(self._widgets):
		# 	data = self._data_list[i]
		# 	assert self._data_list[i] == self.
		# log.debug(utils.method.msg(f"Data count: {data_count}, widget count: {widget_count}"))
		# data_indexes_count_assert = sum(len(indexes) for indexes in self._data_indexes.values())
		# assert len(self._data_ids) == data_indexes_count_assert == len(self._data_list) == len(self._widgets)
		widget_to_update_count = 0
		if widget_count > 0:
			for i, current_data in enumerate(self._data_list):
				data = data_list[i]
				current_data = self._data_list[i]
				if not force:
					if data is current_data: # Don't compare all the data since it is quite expensive. If needed to compare the data in every update, consider manual update call with no data list passed, so it will update all the widgets with the current data and reflect the changes.
						continue
					if data == current_data:
						continue
				widget = self._widgets[i]
				widgets_to_update.append((widget, data, i))
			widget_to_update_count = len(widgets_to_update)
			# type_addition = f" of type '{widgets_to_update[0][0].__class__.__name__}'" if widget_to_update_count > 0 else ""
			# log.debug(utils.method.msg(f"Updating {widget_to_update_count} widgets{type_addition}"))
			for widget, data, i in widgets_to_update:
				# stored_indexes = self._data_id_indexes(data_id)
				# assert stored_indexes is None or current_index > i
				# assert current_index is None or current_index < widget_to_update_count
				# assert data_id not in self._widgets
				# if widget:
				self._update_widget(widget, data, i, *args, **kwargs)
				updated_count += 1
				# self._widgets[i] = weakref.ref(widget) # Already updated. No need to overwrite the widget by itself # TODO: if widget == None?
		# profiler.mark(f"Updated {updated_count} of {widget_count} widgets")
		# log.debug(utils.method.msg(f"Updated {updated_count} of {widget_count} widgets with the goal of {widget_to_update_count}"))
		assert len(self._widgets) == len(self._data_list)
		assert widget_count == data_count
		assert widget_count == len(self._widgets)
		# data_indexes_count_assert = sum(len(indexes) for indexes in self._data_indexes.values())
		# assert len(self._data_ids) == data_indexes_count_assert == len(self._data_list) == len(self._widgets)
		# profiler.print_marks("  			{description} within {timespan} seconds")
		# log.verbose(utils.function.msg(f"				Updated {len(data_list)} widgets within {profiler.measure().timespan} seconds"))
		return updated_count

	def _update_widget(self, widget, data, index, *args, **kwargs):
		widget.update(data, *args, **kwargs)
		# end of if widget
		i = index
		assert widget
		current_data_id = self._data_ids[i]
		current_data = self._data_list[i]
		current_data_id_by_data = self._get_data_id(current_data)
		assert current_data is None or current_data_id == current_data_id_by_data
		removed = self._remove_data_id_index(current_data_id, i)
		assert removed
		# popped_indexes = self._data_indexes.pop(current_data_id)
		# assert popped_index == i
		# popped_widget = self._widgets.pop(current_data_id)()
		self._data_list[i] = data
		# assert current_data_id != data_id # Quite allowed
		data_id = self._get_data_id(data)
		self._data_indexes[data_id].add(i)
		self._data_ids[i] = data_id
		# log.debug(f"	Updated widget: {widget}, data_id: {data_id}, index: {i}, current_data_id: {current_data_id}")
