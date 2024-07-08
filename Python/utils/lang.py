import inspect

import utils.collection.ordered_dict
import utils.inspect_utils as inspect_utils
from utils.log.logger import Logger

log = Logger()

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
		for attr in obj.__dict__.copy():
			log.debug(utils.function.msg_kw(f"Clearing attribute '{attr}'"))
			if attr in obj.__dict__: # Any attribute could have been removed from a desctructor of any other one
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

class NoValueMeta(type):
	def __bool__(cls):
		return False

	def __call__(cls, *args, **kwargs):
		# Prevent instance creation by returning None or raising an exception
		raise TypeError(f"Cannot create instances of {cls.__name__}")

class NoValue(metaclass=NoValueMeta):
	pass