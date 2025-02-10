class NoValue:
	pass

class NotFoundError(Exception):
	def __init__(self, attr_name, message=None):
		default_msg = f"Failed to find attribute '{attr_name}'."
		super().__init__(message or default_msg)
		self.attr_name = attr_name

class Intrstate:
	"""
	Ensures the intrinsic state of an object remains unchanged by storing all user attributes in a separate _state dictionary.
	This approach is useful for representing a data block as an object while concealing control information from the user.
	"""

	def __init__(self, defval=None, *args, **kwargs):
		object.__setattr__(self, '_defval', defval)
		if self._state is None:
			self._state = {}

	def __bool__(self):
		return self._state is not None

	def __getattr__(self, name):
		self_attr = self._get_intrincic_attr(name)
		if self_attr is NoValue:
			if name == '_state':  # Always return None for a non-existing _state to simplify usage
				return None
			state = self._get_intrincic_attr('_state')
			if state is NoValue:
				return self._get_defval('_state')
			value = state.get(name, NoValue)
			return self._process_get_value(name, value)
		return self_attr

	def _get_defval(self, name):
		if self._defval == AttributeError:
			# raise ValueError(f"'{self.__class__.__name__}' object '{self}' has no attribute '{name}'")
			raise NotFoundError(f"'{self.__class__.__name__}' object '{self}' has no attribute '{name}'")
		return self._defval

	def _on_state_update(self, name, value):
		pass

	def _get_intrincic_attr(self, name):
		attr = self.__dict__.get(name, NoValue)
		if attr is NoValue:
			attr = getattr(self.__class__, name, NoValue)
			if isinstance(attr, property):
				return attr.fget(self)
		return attr

	def __setattr__(self, name, value):
		if self._state is None:
			return super().__setattr__(name, value)
		self_attr = self._get_intrincic_attr(name)
		if self_attr is not NoValue:
			raise NotFoundError(f"Cannot set the intrincic attribute '{name}'")
		if value is self._defval:
			if name in self._state:
				del self._state[name]
		else:
			ftocall = self._process_set_value
			result = ftocall(name, value)
			self._state[name] = result
		self._on_state_update(name, value)

	# Override these method to process the value before storing and upon retrieval
	def _process_set_value(self, name, value):
		return value

	def _process_get_value(self, name, value):
		return value if value is not NoValue else self._get_defval(name)
