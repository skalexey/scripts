import importlib.util
import inspect
import os

import utils.string
from utils.collection.ordered_dict import OrderedDict
from utils.log.logger import Logger
from utils.plugin import Plugin

log = Logger()
class PluginManager:
	def __init__(self, plugins_dir, app_context, *args, **kwargs):
		self.plugins_dir = plugins_dir
		self.plugins = OrderedDict()
		self.app_context = app_context
		super().__init__(*args, **kwargs)

	def load_plugins(self):
		log.info(f"Loading plugins from '{self.plugins_dir}'")
		for filename in os.listdir(self.plugins_dir):
			if filename.endswith(".py") and filename != "__init__.py":
				plugin_name = os.path.splitext(filename)[0]
				plugin_module = importlib.import_module(f"{self.plugins_dir}.{plugin_name}")
				classname = utils.string.to_camel_case(plugin_name)
				cls = getattr(plugin_module, classname, None)
				if cls is None:
					raise ValueError(f"Couldn't find class '{classname}' in the module of the plugin '{plugin_name}'")
				if not inspect.isclass(cls):
					raise ValueError(f"'{classname}' must be a class to be a plugin")
				bases = getattr(cls, '__bases__', None)
				if not bases and Plugin not in bases:
					raise ValueError(f"Plugin class '{classname}' must inherit from Plugin")
				# Check if the plugin name ends with "_plugin"
				if not plugin_name.endswith("_plugin"):
					raise ValueError(f"Plugin name '{plugin_name}' must end with '_plugin'")
				log.info(f" Loading plugin '{plugin_name}'")
				inst = cls(self.app_context)
				self.plugins[plugin_name] = inst

	def get_plugin(self, name):
		return self.plugins.get(name)
