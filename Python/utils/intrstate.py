class Intrstate:
	def __init__(self, *args, **kwargs):
		if self._state is None:
			self._state = {}
		super().__init__(*args, **kwargs)

	def __bool__(self):
		return self._state is not None

	def __getattr__(self, name):
		self_attr = self._get_intrincic_attr(name)
		if self_attr is not None:
			return self_attr
		if name == '_state':
			return None
		state = self._get_intrincic_attr('_state')
		if state is None:
			return None
		return state.get(name)

	def _on_state_update(self, name, value):
		pass

	def _get_intrincic_attr(self, name):
		attr = self.__dict__.get(name, None)
		if attr is not None:
			return attr
		attr = getattr(self.__class__, name, None)
		if isinstance(attr, property):
			return attr.fget(self)
		return None

	def __setattr__(self, name, value):
		if self._state is None:
			return super().__setattr__(name, value)
		self_attr = self._get_intrincic_attr(name)
		if self_attr is not None:
			raise AttributeError(f"Cannot set the intrincic attribute '{name}'")
		if value is None:
			del self._state[name]
		else:
			self._state[name] = value
		self._on_state_update(name, value)
