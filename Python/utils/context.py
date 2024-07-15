# Base class for any application or other global context
class GlobalContextMeta(type):
	def __getattr__(cls, name):
		for subclass in cls.__subclasses__():
			attr = getattr(subclass, name, None)
			if attr is not None:
				return attr
		raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")

class GlobalContext(metaclass=GlobalContextMeta):
	def __setattr__(self, name, value):
		setattr(self.__class__, name, value)
		# You can add custom logic here
		super().__setattr__(name, value)