import inspect
from abc import ABCMeta

import utils.function
import utils.inspect_utils


def class_path(cls_or_name):
	if inspect.isclass(cls_or_name):
		cls = cls_or_name
	elif isinstance(cls_or_name, str):
		frame = utils.inspect_utils.caller_frame()
		cls = find_class(cls_or_name, globals=frame.f_globals)
		if cls is None:
			raise ValueError(utils.function.msg(f"Couldn't find class '{cls_or_name}' in globals() on the call level nor in __builtins__"))
	else:
		raise ValueError(utils.function.msg(f"Expected class or class name, got {cls_or_name}"))
	return f"{cls.__module__}.{cls.__qualname__}"

def class_name(cls_or_path):
	if isinstance(cls_or_path, str):
		return cls_or_path.split('.')[-1]
	else:
		return cls_or_path.__name__


def find_class(class_path_or_name, globals=None): # e.g. 'module.submodule.ClassName'
	classname = class_name(class_path_or_name)
	classpath = class_path_or_name if classname != class_path_or_name else None
	frame = utils.inspect_utils.caller_frame()
	_globals = globals or frame.f_globals
	if classname in _globals:
		cls = _globals[classname]
	elif classname in __builtins__:
		cls = __builtins__[classname]
	else:
		return None
	if classpath is not None:
		found_class_path = class_path(cls)
		if found_class_path != classpath:
			return None
	return cls

class EnforcedABCMeta(ABCMeta):
	"""
	Helper class for situations when one of the inherited classes suppresses ABCMeta (e.g. QWidget).
	"""
	def __call__(cls, *args, **kwargs):
		# Check if abstract methods are implemented
		def check_abstractmethod(name, value):
			if getattr(value, "__isabstractmethod__", False):
				raise TypeError(f"Can't instantiate abstract class '{cls.__name__}' with not defined abstract method '{name}'")
		for name, value in cls.__dict__.items():
			check_abstractmethod(name, value)
			if name == '__abstractmethods__':
				for abstract_method in value:
					check_abstractmethod(abstract_method, getattr(cls, abstract_method))
		super_obj = super() # For debugging super_obj.__thisclass__.__mro__[1]
		return super_obj.__call__(*args, **kwargs)
	
def method_list(cls):
	"""
	Get a list of method names declared directly in a class (excluding inherited methods).

	Args:
		cls: The class to inspect.

	Returns:
		A list of method names defined in the class.
	"""
	return [
		name
		for name, value in inspect.getmembers(cls, predicate=inspect.isfunction)
		if value.__qualname__.startswith(cls.__name__ + ".")
	]
