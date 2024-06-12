import json
from abc import ABC

from utils.decorators import no_return
from utils.profile.trackable_resource import *


class Module(TrackableResource, ABC):
	def __init__(self, module_name, *args, **kwargs):
		assert isinstance(module_name, str)
		self.module_name = module_name
		self._settings = None

	# No need to call this class on_* methods in derived classes. It is done automatically by the module manager.
	def call_if_defined(self, method_name, *args, **kwargs):
		self.app_context.module_manager.call_on_module(self, method_name, *args, **kwargs)

	# Settings interface.
	# Every module stores its settings in a dedicated object of the settings file under the key with module's name.
	def module_settings(self):
		if self._settings is None:
			self.load_settings()
		return self._settings
	
	def get_setting(self, key, default=None):
		module_settings = self.module_settings()
		return module_settings.get(key, default)
	
	def settings_file_path(self):
		return f"{self.module_name}_settings.json"

	def store_settings(self):
		fpath = self.settings_file_path()
		with open(fpath, "w") as f:
			settings = self.module_settings()
			json.dump(settings, f, indent='\t')

	def load_settings(self):
		fpath = self.settings_file_path()
		try:
			with open(fpath, 'r') as file:
				self._settings = json.load(file)
		except FileNotFoundError:
			self._settings = {}
		except Exception as e:
			print(f"Error loading settings: '{e}'")
			raise e

	def set_setting(self, key, value):
		module_settings = self.module_settings()
		module_settings[key] = value
		return True

	# TODO: support a path as array of keys
	def update_setting(self, key, value):
		if not self.set_setting(key, value):
			return False
		return self.store_settings()

	def define_setting(self, name, default, getter=None, setter=None) -> None:
		value = self.get_setting(name, default)
		private_name = self._setting_private_variable_name(name)
		# Generate the private variable
		setattr(self, private_name, None)
		setter_override_name = f"set_{name}"
		getter_override_name = f"get_{name}"

		if setter is None:
			if hasattr(self, setter_override_name):
				def setter_func(self, value):
					getattr(self, setter_override_name)(value)
			else:
				setter_func = self._gen_setting_setter(name)
		else:
			setter_func = setter

		if getter is None:
			if hasattr(self, getter_override_name):
				def getter_func(self):
					return getattr(self, getter_override_name)()
			else:
				getter_func = self._gen_setting_getter(name)
		else:
			getter_func = getter
		
		# Create a property with the getter and setter
		prop = property(getter_func, setter_func)
		
		# Set the property to the class instance
		setattr(self.__class__, name, prop)
		if value is not None:
			# Assign the default value to the property
			setattr(self, name, value)

	def _set_defined_setting_by_name_base(self, name, value, update_setting_func=None):
		filter_func_name = f"{name}_setter_filter"
		if hasattr(self, filter_func_name):
			filtered_value = getattr(self, filter_func_name)(value)
		else:
			filtered_value = value
		self._set_setting_private_variable(name, filtered_value)
		on_set_name = f"on_{name}_set"
		if hasattr(self, on_set_name):
			getattr(self, on_set_name)(filtered_value)
		current_value = self.get_setting(name)
		if current_value == filtered_value:
			return False
		_update_setting_func = update_setting_func if update_setting_func is not None else self.update_setting
		if not _update_setting_func(name, filtered_value):
			return False
		on_changed_name = f"on_{name}_changed"
		if hasattr(self, on_changed_name):
			getattr(self, on_changed_name)(filtered_value)
		return True

	def _get_defined_setting_by_name(self, name):
		private_name = self._setting_private_variable_name(name)
		return getattr(self, private_name)

	def _setting_private_variable_name(self, name):
		return f"_{name}"
		
	def _set_setting_private_variable(self, name, value):
		private_name = self._setting_private_variable_name(name)
		setattr(self, private_name, value)

	def _gen_setting_setter(self, name):
		def setter(self, value):
			self._set_defined_setting_by_name_base(name, value)
		return setter

	def _gen_setting_getter(self, name):
		def getter(self):
			return self._get_defined_setting_by_name(name)
		return getter
