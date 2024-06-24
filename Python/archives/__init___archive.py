import importlib
import inspect
import os

# Directory path of the current module
current_dir = os.path.dirname(__file__)

# Cache for storing loaded objects (functions, classes, and variables)
_loaded_objects = {}

# Mapping of object names to their respective module paths
_object_to_module = {}

# Loop through all files in the current directory to register valid object names
for filename in os.listdir(current_dir):
	if filename.endswith(".py") and filename != "__init__.py":
		module_name = filename[:-3]
		module_path = f"{__name__}.{module_name}"
		module = importlib.import_module(module_path)
		for name, obj in inspect.getmembers(module):
			if inspect.isfunction(obj) or inspect.isclass(obj) or not name.startswith("__"):
				_object_to_module[name] = module_path

def __getattr__(name):
	# Check if the requested object is registered
	if name in _object_to_module:
		# If the object is already loaded, return it from the cache
		if name in _loaded_objects:
			return _loaded_objects[name]
		
		# Dynamically import the module containing the requested object
		module_path = _object_to_module[name]
		module = importlib.import_module(module_path)
		
		# Fetch the object from the module
		obj = getattr(module, name)
		
		# Cache the loaded object
		_loaded_objects[name] = obj
		
		return obj

	# If the object is not found, raise AttributeError
	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Expose all valid object names as part of the module's public API
__all__ = list(_object_to_module.keys())
