import time
import weakref

from utils.collection.associative_list import AssociativeList
from utils.log.logger import Logger

log = Logger()

class TrackableResourceInfo:
	def __init__(self):
		self.id = None
		self.ref = None
		self.on_destroyed = None
		self._repr = None
		self._created_time = time.time()

	@property
	def repr(self):
		obj = self.ref()
		if obj is not None:
			address = hex(id(obj))
			self._repr = f"{obj!r} address={address}" # Always store the latest repr
		return self._repr
	
	@property
	def lifetime(self):
		return time.time() - self._created_time

	@property
	def info(self):
		return self.repr # By default. Opened for further improvements.
	
	def __repr__(self):
		return f"{self.__class__.__name__}(id={self.id}, repr={self.repr}, lifetime={self.lifetime})"


class TrackableResource:
	"""
	Enables visibility into the creation and destruction of derived class objects by automatically printing verbose log messages, and allowing to assign a custom function to be executed upon object destruction.
	"""

	resources = AssociativeList()

	def __repr__(self):
		super_repr = super().__repr__()
		_memid = id(self)
		return f"{self.__class__.__name__}(memid={_memid}{super_repr})"

	def __init__(self, on_destroyed=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		info = TrackableResourceInfo()
		info.on_destroyed = on_destroyed
		def _on_destroyed(ref):
			log.verbose(f"TrackableResource destroyed: '{info.repr}'")
			if info.on_destroyed is not None:
				info.on_destroyed(info)
			TrackableResource.resources.remove(info.id)
		info.ref = weakref.ref(self, _on_destroyed)
		info.id = self.resources.add(info)
		log.verbose(f"TrackableResource created: '{info.repr}'")
