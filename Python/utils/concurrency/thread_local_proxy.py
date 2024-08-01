import threading

from utils.memory.weakly_allocated import WeaklyAllocated


class ThreadLocalProxy(WeaklyAllocated):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@property
	def _obj(self):
		obj = getattr(self._wobj, "inst", None)
		if obj is None:
			obj = self._allocator(*self._args, **self._kwargs)
			self._wobj.inst = obj
		return obj

	@_obj.setter
	def _obj(self, value):
		tloc = self.__dict__.get("_wobj")
		if tloc is None:
			tloc = threading.local()
			object.__setattr__(self, "_wobj", tloc)
		tloc.inst = value
