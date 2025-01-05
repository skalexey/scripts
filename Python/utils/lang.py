import utils.function
from utils.log.logger import Logger

log = Logger()

def is_primitive(value):
	return isinstance(value, (int, float, str, bool, bytes))

def extract_self(bound_method):
	return getattr(bound_method, '__self__', None)

def clear_resources(obj):
	"""
	Sets all the attributes of an object to None, or call obj.clear() if obj is a dictionary. Useful for triggering garbage collection in the case of circular references.
	"""
	if isinstance(obj, dict):
		obj.clear()
	else:
		for attr in obj.__dict__.copy():
			log.verbose(utils.function.msg_kw(f"Clearing attribute '{attr}'"))
			if attr in obj.__dict__: # Any attribute could have been removed from a desctructor of any other one
				obj.__dict__[attr] = None

class NoValueMeta(type):
	def __bool__(cls):
		return False

	def __call__(cls, *args, **kwargs):
		# Prevent instance creation by returning None or raising an exception
		raise TypeError(f"Cannot create instances of {cls.__name__}")

class NoValue(metaclass=NoValueMeta):
	"""
	This class itself represents a value that has not been set. Useful for default arguments where None is a valid value.
	"""
	pass


class SafeSuper:
	"""
	Used in safe_super() as the return value.
	It does not support super() without arguments for performance reasons since retrieving the class of the function requires iterating the whole MRO.
	"""

	class DummyFunct:
		def __init__(self, *args, **kwargs):
			pass

	def __init__(self, cls, inst):
		self._super = super(cls, inst)

	def __getattr__(self, name):
		return getattr(self._super, name, self.DummyFunct)
	
def safe_super(cls, inst):
	"""
	An extended version of super(), designed to prevent exceptions when called at the final point in the MRO.
	Reduces coupling by abstracting away uncertainties in the class hierarchy.
	"""
	return SafeSuper(cls, inst)

def getattr_noexcept(obj, name, default=NoValue):
	return obj.__dict__.get(name, default)

def compare_exceptions(e1, e2):
	return type(e1) == type(e2) and e1.args == e2.args
	

def safe_enter(func):
	"""
	Decorator for __enter__ that ensures __exit__ is always called even in the case of an exception in __enter__.
	Re-raises the exception after calling __exit__.

	Usage example:
	@safe_enter
	def __enter__(self):
	"""

	def wrapper(self):
		try:
			return func(self)
		except Exception as e:
			self.__exit__(type(e), e, e.__traceback__)
			raise
	return wrapper
