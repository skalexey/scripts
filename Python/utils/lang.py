import utils.function
from utils.log.logger import Logger

log = Logger()

def is_primitive(value):
	return isinstance(value, (int, float, str, bool, bytes))

def extract_self(bound_method):
	return getattr(bound_method, '__self__', None)

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


# It does not support super() without arguments for performance reasons since retrieving the class of the function requires iterating the whole MRO.
class SafeSuper:
	class DummyFunct:
		def __init__(self, *args, **kwargs):
			pass

	def __init__(self, cls, inst):
		self._super = super(cls, inst)

	def __getattr__(self, name):
		return getattr(self._super, name, self.DummyFunct)
	
def safe_super(cls, inst):
	return SafeSuper(cls, inst)

def getattr_noexcept(obj, name, default=NoValue):
	return obj.__dict__.get(name, default)

def compare_exceptions(e1, e2):
	return type(e1) == type(e2) and e1.args == e2.args
	

# Safe __enter__ decorator that catches exceptions and calls __exit__ upon encountering one, then re-raises the exception
# Example usage:
# @safe_enter
# def __enter__(self):
def safe_enter(func):
	def wrapper(self):
		try:
			return func(self)
		except Exception as e:
			self.__exit__(type(e), e, e.__traceback__)
			raise
	return wrapper


class StaticProperty:
	def __init__(self, fget=None, fset=None):
		self.fget = fget
		self.fset = fset

	def __get__(self, instance, owner):
		if self.fget is None:
			raise AttributeError("unreadable attribute")
		return self.fget(owner)

	def __set__(self, instance, value):
		if self.fset is None:
			raise AttributeError("can't set attribute")
		self.fset(instance.__class__, value)

	def getter(self, fget):
		self.fget = fget
		return self

	def setter(self, fset):
		self.fset = fset
		return self
