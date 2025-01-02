from utils.proxy import Proxy

"""
Acts as a proxy for an object of a specified class, but created only upon first use.
It stores a reference to the class or an allocating function, along with the arguments to be passed during instantiation.
"""
class LazyAllocated(Proxy):
	def __init__(self, allocator=None, *args, **kwargs):
		super().__init__(None) # Triggers _obj.setter through object.__setattr__
		object.__setattr__(self, "_allocator", allocator)
		object.__setattr__(self, "_args", args)
		object.__setattr__(self, "_kwargs", kwargs)

	@property
	def _obj(self):
		if self._wobj is None:
			wobj = self._allocator(*self._args, **self._kwargs)
			object.__setattr__(self, "_wobj", wobj)
		return self._wobj

	@_obj.setter
	def _obj(self, value):
		object.__setattr__(self, "_wobj", value)
