import inspect

import utils.collection.ordered_dict
import utils.inspect_utils as inspect_utils


def is_primitive(value):
	return isinstance(value, (int, float, str, bool, bytes))

def extract_self(bound_method):
	if hasattr(bound_method, '__self__'):
		return bound_method.__self__
	return None

def clear_resources(obj):
	if isinstance(obj, dict):
		obj.clear()
	else:
		for attr in obj.__dict__:
			obj.__dict__[attr] = None

class DefaultNew:
	def __init__(self, callable, *args, **kwargs):
		self._callable = callable
		self._args = args
		self._kwargs = kwargs

	def __get__(self, instance, owner):
		if instance is None:
			return self
		else:
			return self._callable(*self._args, **self._kwargs)

def defnew(callable, *args, **kwargs):
	return DefaultNew(callable, *args, **kwargs)
