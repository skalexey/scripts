class WeakCallable:
	def __init__(self, cb, owner=None, *args, **kwargs):
		def on_destroyed(ref):
			log.verbose(f"Callable has been garbage collected")
		if owner is not None:
			weakcbs = getattr(owner, "__weakcbs__", None)
			if weakcbs is None:
				weakcbs = []
				owner.__weakcbs__ = weakcbs
			weakcbs.append(cb)
			owner_ref = weakref.ref(owner)
			def remove_from_owner():
				owner = owner_ref()
				if owner is not None:
					weakcbs.remove(self)
					if len(weakcbs) == 0:
						del weakcbs
			on_destroyed_base = on_destroyed
			def on_destroyed(ref):
				on_destroyed_base(ref)
				owner = owner_ref()
				if owner is not None:
					log.verbose(f"Removing weak callable from the owner '{owner}'")
					weakcbs = owner.__weakcbs__
					weakcbs.remove(self)
					if len(weakcbs) == 0:
						del owner.__weakcbs__
				else:
					log.verbose(f"Owner has been garbage collected")
		self._ref = weakref.ref(cb, on_destroyed)
		super().__init__(*args, **kwargs)

	def __call__(self, *args, **kwargs):
		cb = self._ref()
		if cb is None:
			raise RuntimeError('Callable has been garbage collected')
		return cb(*args, **kwargs)
