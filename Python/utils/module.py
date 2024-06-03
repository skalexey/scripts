import json
from abc import ABC


class Module(ABC):
	def __init__(self, name, *args, **kwargs):
		assert(isinstance(name, str))
		self.name = name
		self._settings = None

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
		return f"{self.name}_settings.json"

	def store_settings(self):
		fpath = self.settings_file_path()
		with open(fpath, "w") as f:
			settings = self.module_settings()
			json.dump(settings, f)

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

	# TODO: support a path as array of keys
	def update_setting(self, key, value):
		self.set_setting(key, value)
		self.store_settings()

	def define_setting(self, name, default, getter=None, setter=None):
		value = self.get_setting(name, default)
		private_name = self._setting_private_variable_name(name)
		# Generate the private variable
		setattr(self, private_name, value)
		
		getter_func = getter if getter is not None else self._gen_setting_getter(name)
		setter_func = setter if setter is not None else self._gen_setting_setter(name)
		
		# Create a property with the getter and setter
		prop = property(getter_func, setter_func)
		
		# Set the property to the class instance
		setattr(self.__class__, name, prop)

	def _set_setting_by_name(self, name, value):
		current_value = self._get_setting_by_name(name)
		if current_value == value:
			assert(current_value == self.get_setting(name))
			return False
		self._set_setting_private_variable(name, value)
		self.update_setting(name, value)
		return True

	def _get_setting_by_name(self, name):
		private_name = self._setting_private_variable_name(name)
		return getattr(self, private_name)

	def _setting_private_variable_name(self, name):
		return f"_{name}"
		
	def _set_setting_private_variable(self, name, value):
		private_name = self._setting_private_variable_name(name)
		setattr(self, private_name, value)

	def _gen_setting_setter(self, name):
		def setter(self, value):
			self._set_setting_by_name(name, value)
		return setter

	def _gen_setting_getter(self, name):
		def getter(self):
			return self._get_setting_by_name(name)
		return getter
