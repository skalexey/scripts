# Base class for any application or other global context
class GlobalContextMeta(type):
	def __getattr__(cls, name):
		for subclass in cls.__subclasses__():
			if hasattr(subclass, name):
				return getattr(subclass, name)
		raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

class GlobalContext(metaclass=GlobalContextMeta):
	pass