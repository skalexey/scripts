import weakref

from utils.memory import WeakProxy, deref_if_weak_proxy, wrap_weakable


class WeakList:
	def __init__(self, data=None):
		self._data = []
		if data:
			self.extend(data)

	def __eq__(self, other):
		return self._data == other

	def __getattr__(self, name):
		return getattr(self._data, name)

	def __setitem__(self, key, value):
		self._data[key] = wrap_weakable(value)

	def __getitem__(self, key):
		return deref_if_weak_proxy(self._data[key])
	
	def __iter__(self):
		return (deref_if_weak_proxy(item) for item in self._data)

	def append(self, item):
		self._data.append(wrap_weakable(item))

	def insert(self, index, item):
		self._data.insert(index, wrap_weakable(item))

	def extend(self, items):
		self._data.extend(wrap_weakable(item) for item in items)
