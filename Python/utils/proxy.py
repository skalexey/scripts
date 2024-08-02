class Proxy:
	def __init__(self, obj):
		super().__setattr__("_obj", obj)

	def __getattr__(self, name):
		return object.__getattribute__(self._obj, name)

	def __setattr__(self, name, value):
		setattr(self._obj, name, value)

	def __delattr__(self, name):
		delattr(self._obj, name)

	def __call__(self, *args, **kwargs):
		return self._obj(*args, **kwargs)

	def __instancecheck__(self, instance):
		return isinstance(self._obj, instance)