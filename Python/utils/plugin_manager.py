import importlib.util
import os

from utils.log.logger import *
from utils.ordered_dict import *
from utils.plugin import *

log = Logger("plugin_manager")
class PluginManager:
	def __init__(self, plugins_dir, app_context):
		self.plugins_dir = plugins_dir
		self.plugins = OrderedDict()
		self.app_context = app_context

	def load_plugins(self):
		log.info(f"Loading plugins from '{self.plugins_dir}'")
		for filename in os.listdir(self.plugins_dir):
			if filename.endswith(".py") and filename != "__init__.py":
				plugin_name = os.path.splitext(filename)[0]
				plugin_module = importlib.import_module(f"{self.plugins_dir}.{plugin_name}")
				for name in dir(plugin_module):
					obj = getattr(plugin_module, name)
					if hasattr(obj, '__bases__') and Plugin in obj.__bases__:
						# Check if the plugin name ends with "_plugin"
						if not plugin_name.endswith("_plugin"):
							raise ValueError(f"Plugin name '{plugin_name}' must end with '_plugin'")
						log.info(f" Loading plugin '{plugin_name}'")
						inst = obj(plugin_name, self.app_context)
						self.plugins[plugin_name] = inst

	def get_plugin(self, name):
		return self.plugins.get(name)