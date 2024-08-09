import json
from abc import ABC

import utils.inspect_utils as inspect_utils
import utils.lang
import utils.serialize
import utils.string
from utils.log.logger import Logger
from utils.profile.trackable_resource import TrackableResource

log = Logger()

class Module(TrackableResource, ABC):
	def __init__(self, module_name=None, *args, **kwargs):
		def on_destroyed(info):
			log.debug(f"Module destroyed: {info.repr}")
		super().__init__(on_destroyed=on_destroyed, *args, **kwargs)
		assert isinstance(module_name, (str, type(None)))
		self._module_name = module_name
		self._settings = None

	@property
	def classname(self):
		return self.__class__.__name__

	@property
	def module_name(self):
		if self._module_name is None: # Default module name is the class name without the "Module" converted to snake case.
			id = utils.string.to_snake_case(self.classname)
			self._module_name = id.replace("_module", "")
			return self._module_name
		return self._module_name

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
		return f"data/{self.module_name}_settings.json"

	def store_settings(self):
		fpath = self.settings_file_path()
		return utils.serialize.to_json(self.module_settings(), fpath=fpath)

	def load_settings(self):
		fpath = self.settings_file_path()
		self._settings = utils.serialize.from_json(fpath=fpath) or {}

	def set_setting(self, key, value):
		module_settings = self.module_settings()
		module_settings[key] = value
		return True

	# TODO: support a path as array of keys
	def update_setting(self, key, value):
		if not self.set_setting(key, value):
			return False
		return self.store_settings()

	def define_setting(self, name, default, current_value=None, getter=None, setter=None) -> None:
		value = current_value if current_value is not None else self.get_setting(name, default)
		private_name = self._setting_private_variable_name(name)
		# Generate the private variable
		setattr(self, private_name, None)
		setter_override_name = f"set_{name}"
		getter_override_name = f"get_{name}"

		if setter is None:
			attr = getattr(self, setter_override_name, None)
			setter_func = inspect_utils.function(attr) if attr is not None else self._gen_setting_setter(name)
		else:
			setter_func = setter

		if getter is None:
			attr = getattr(self, getter_override_name, None)
			getter_func = inspect_utils.function(attr) if attr is not None else self._gen_setting_getter(name)
		else:
			getter_func = getter
		
		# Create a property with the getter and setter
		prop = property(getter_func, setter_func)
		
		# Set the property to the class instance
		setattr(self.__class__, name, prop)
		if value is not None:
			# Assign the value to the property and trigger the setter
			setattr(self, name, value)

	# current_value - used to override the current value getting logic that prevents from triggering on_setting_changed and storing settings if the setting has not been changed.
	# By default, it takes the setting value from the main settings file through the settings_manager.
	def _set_defined_setting_by_name_base(self, name, value, current_value=None, update_setting_func=None):
		filter_func_name = f"{name}_setter_filter"
		attr = getattr(self, filter_func_name, None)
		if attr is not None:
			filtered_value = attr(value)
		else:
			filtered_value = value
		self._set_setting_private_variable(name, filtered_value)
		on_set_name = f"on_{name}_set"
		attr = getattr(self, on_set_name, None)
		if attr is not None:
			attr(filtered_value)
		_current_value = current_value if current_value is not None else self.get_setting(name)
		if _current_value == filtered_value:
			return False # No need to update the setting if it is the same
		_update_setting_func = update_setting_func if update_setting_func is not None else self.update_setting
		if not _update_setting_func(name, filtered_value):
			return False
		on_changed_name = f"on_{name}_changed"
		attr = getattr(self, on_changed_name, None)
		if attr is not None:
			attr(filtered_value)
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
