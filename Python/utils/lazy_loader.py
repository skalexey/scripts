import importlib
import inspect
import os

import utils.function
import utils.inspect_utils
import utils.string
from utils.log.logger import Logger

log = Logger()

class LazyLoader:
	def __init__(self, *args, **kwargs):
		self._module_names = None
		# Cache for storing loaded objects (functions, classes, and variables)
		self._loaded_objects = {}
		# Mapping of object names to their respective module paths
		self._object_to_module = {}
		super().__init__(*args, **kwargs)
		self._user_module_name = None

	@property
	def user_module_name(self):
		if self._user_module_name is None:
			user_frame_info = utils.inspect_utils.user_frame_info()
			module = inspect.getmodule(user_frame_info.frame)
			self._user_module_name = module.__name__
		return self._user_module_name

	def collect_module_names(self):
		from utils.collection.ordered_set import OrderedSet
		module_names = OrderedSet()
		# Directory path of the current module
		user_frame_info = utils.inspect_utils.user_frame_info()
		user_file = user_frame_info.filename
		user_dir = os.path.dirname(user_file)

		# Loop through all files in the current directory to register valid object names
		for filename in os.listdir(user_dir):
			if filename.endswith(".py") and filename != "__init__.py":
				module_name = filename[:-3]
				module_names.add(module_name)
		return module_names

	def _module_path(self, module_name):
		user_frame_info = utils.inspect_utils.user_frame_info()
		module = inspect.getmodule(user_frame_info.frame)
		return f"{self.user_module_name}.{module_name}"

	def import_module(self, module_name):
		log(self.msg(f"importing module: '{module_name}'"))
		module_path = self._module_path(module_name)
		module = importlib.import_module(module_path)
		for name, obj in inspect.getmembers(module):
			if name.startswith("__"):
				continue
			if inspect.isfunction(obj) or inspect.isclass(obj) or not name.startswith("__"):
				self._object_to_module[name] = module_path

	def import_modules(self):
		self._object_to_module = {}
		# Loop through all files in the current directory to register valid object names
		for module_name in self._module_names:
			self.import_module(module_name)
		# Expose all valid object names as part of the module's public API
		__all__ = list(self._object_to_module.keys())

	def raise_attribute_error(self, name):
		raise AttributeError(utils.function.msg(self.msg(f"Object '{name}' not found")))

	def msg(self, message):
		return f"from module '{self.user_module_name}': {message}"

	def get(self, name):
		if name == '__wrapped__':
			return None

		if name.startswith("__"):
			self.raise_attribute_error(name)

		# Check if the requested object is registered
		module_path = self._object_to_module.get(name)

		if module_path is None:
			# Try to interpert it as a class module
			to_module_name = utils.string.to_snake_case(name)
			if self._module_names is None:
				self._module_names = self.collect_module_names()
			if to_module_name in self._module_names:
				module_path = self._module_path(to_module_name)

		if module_path is None:
			# Load and register all the modules
			self.import_modules()
			module_path = self._object_to_module.get(name)

		if module_path is None:
			# If the object is not found, raise AttributeError
			log.warning(self.msg(f"Object '{name}' not found"))
			return None

		# If the object is already loaded, return it from the cache
		if name in self._loaded_objects:
			return self._loaded_objects[name]
		
		# Dynamically import the module containing the requested object
		module = importlib.import_module(module_path)
		
		# Fetch the object from the module
		obj = getattr(module, name)
		
		# Cache the loaded object
		self._loaded_objects[name] = obj
		
		return obj
