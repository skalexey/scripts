import importlib

import utils.class_utils as class_utils


def find_or_import_class(class_path): # e.g. 'module.submodule.ClassName'
	# Try to find the class in globals()
	cls = class_utils.find_class(class_path)
	if cls:
		return cls
	# If not found in globals(), attempt to import the module and retrieve the class
	module_name, class_name = class_path.rsplit('.', 1)
	try:
		module = importlib.import_module(module_name)
		return getattr(module, class_name)
	except (ImportError, AttributeError, ValueError) as e:
		raise ValueError(f"Error finding or importing class '{class_name}': {str(e)}")
