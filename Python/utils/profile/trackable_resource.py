import weakref

import utils.method
from utils.log.logger import Logger

log = Logger()

class TrackableResource:
	def __repr__(self):
		super_repr = super().__repr__()
		_memid = id(self)
		return f"{self.__class__.__name__}(memid={_memid}{super_repr})"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		log.verbose(utils.function.msg_v())
		identifier = f"TrackableResource: {self!r}"
		def on_destroyed():
			log.verbose(utils.function.msg(identifier))
		self._finalizer = weakref.finalize(self, on_destroyed)
