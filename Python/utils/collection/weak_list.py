from utils.log.logger import Logger
from utils.memory import deref_if_weak_proxy, wrap_weakable

log = Logger()

class WeakList:
	def __init__(self, data=None, on_destroyed=None):
		self._data = []
		self._on_destroyed = on_destroyed
		if data:
			self.extend(data)

	def _wrap_weakable(self, item, object_id, index):
		on_destroyed = self._gen_finalizer(object_id, index) if self._on_destroyed else None
		return wrap_weakable(item, on_destroyed=on_destroyed)

	def _gen_finalizer(self, object_id, index):
		def finalizer(ref, object_id=object_id, on_destroyed=self._on_destroyed):
			log.debug(f"WeakList: on_destroyed: object_id={object_id}, index={index}")
			on_destroyed(object_id, index)
		return finalizer

	def __eq__(self, other):
		if other is None:
			return False
		if len(self) != len(other):
			return False
		for i, item in enumerate(self):
			comparable = other[i]
			if item is comparable:
				continue
			if item != comparable:
				return False
		return True

	def __getattr__(self, name):
		return getattr(self._data, name)

	def __setitem__(self, key, value):
		self._data[key] = self._wrap_weakable(value, id(value), key)

	def __getitem__(self, key):
		return deref_if_weak_proxy(self._data[key])
	
	def __iter__(self):
		return (deref_if_weak_proxy(item) for item in self._data)
	
	def __len__(self):
		return len(self._data)

	def append(self, item):
		self._data.append(self._wrap_weakable(item, id(item), len(self._data)))

	def insert(self, index, item):
		self._data.insert(index, self._wrap_weakable(item, id(item), index))

	def extend(self, items):
		self._data.extend(self._wrap_weakable(item, id(item), i) for i, item in enumerate(items))

	def pop(self, index=-1):
		return deref_if_weak_proxy(self._data.pop(index))
