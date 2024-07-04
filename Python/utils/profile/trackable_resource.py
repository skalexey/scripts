import weakref

import utils.method
from utils.collection.associative_list import AssociativeList
from utils.log.logger import Logger

log = Logger()

class TrackableResourceInfo:
	def __init__(self):
		self.id = None
		self.ref = None
		self._repr = None

	@property
	def repr(self):
		obj = self.ref()
		if obj is not None:
			self._repr = f"TrackableResource: {obj!r}" # Always store the latest repr
		return self._repr

class TrackableResource:
	resources = AssociativeList()
	def __repr__(self):
		super_repr = super().__repr__()
		_memid = id(self)
		return f"{self.__class__.__name__}(memid={_memid}{super_repr})"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		info = TrackableResourceInfo()
		def on_destroyed(ref):
			log.verbose(utils.function.msg(info.repr))
			TrackableResource.resources.remove(info.id)
		info.ref = weakref.ref(self, on_destroyed)
		info.id = self.resources.add(info)
		log.verbose(utils.function.msg_v())
