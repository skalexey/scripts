import importlib

import utils.class_utils as class_utils


def find_class(class_path): # e.g. 'module.submodule.ClassName'
	module_name, class_name = class_path.rsplit('.', 1)
	if class_name in globals():
		cls = globals()[class_name]
	elif class_name in __builtins__:
		cls = __builtins__[class_name]
	else:
		return None
	cls_path = class_utils.class_path(cls)
	if cls_path == class_path:
		return cls
	return None

def find_or_import_class(class_path): # e.g. 'module.submodule.ClassName'
	# Try to find the class in globals()
	cls = find_class(class_path)
	if cls:
		return cls
	# If not found in globals(), attempt to import the module and retrieve the class
	try:
		module_name, class_name = class_path.rsplit('.', 1)
		module = importlib.import_module(module_name)
		return getattr(module, class_name)
	except (ImportError, AttributeError, ValueError) as e:
		raise ValueError(f"Error finding or importing class '{class_name}': {str(e)}")
