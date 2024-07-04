
import weakref

import utils.lang
from utils.log.logger import Logger

log = Logger()

class WeakCallable:
	def __init__(self, cb, owner=None, *args, **kwargs):
		def on_destroyed(ref):
			log.warning(f"Callable has been garbage collected")
		if owner is not None:
			if not hasattr(owner, "__weakcbs__"):
				owner.__weakcbs__ = []
			owner.__weakcbs__.append(cb)
			owner_ref = weakref.ref(owner)
			def remove_from_owner():
				owner = owner_ref()
				if owner is not None:
					owner.__weakcbs__.remove(self)
					if len(owner.__weakcbs__) == 0:
						del owner.__weakcbs__
			on_destroyed_base = on_destroyed
			def on_destroyed(ref):
				on_destroyed_base(ref)
				owner = owner_ref()
				if owner is not None:
					log.debug(f"Removing weak callable from the owner '{owner}'")
					owner.__weakcbs__.remove(self)
					if len(owner.__weakcbs__) == 0:
						del owner.__weakcbs__
				else:
					log.debug(f"Owner has been garbage collected")
		self._ref = weakref.ref(cb, on_destroyed)
		super().__init__(*args, **kwargs)

	def __call__(self, *args, **kwargs):
		cb = self._ref()
		if cb is None:
			raise RuntimeError('Callable has been garbage collected')
		return cb(*args, **kwargs)
