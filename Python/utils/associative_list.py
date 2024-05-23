from utils.ordered_dict import *

class AssociativeList():
	def __init__(self):
		self._data = OrderedDict()
		self._id = 0

	def __getitem__(self, index):
		return self._data.at(index)
	
	def __setitem__(self, index, value):
		key = self._data.key_at(index)
		self._data[key] = value

	def __len__(self):
		return len(self._data)
	
	def __iter__(self):
		return iter(self._data)
	
	def __contains__(self, key):
		return key in self._data
	
	def __delitem__(self, key):
		del self._data[key]

	def copy(self):
		new = AssociativeList()
		new._data = self._data.copy()
		new._id = self._id
		return new

	def clear(self):
		self._data.clear()

	def keys(self):
		return self._data.keys()

	def values(self):
		return self._data.values()

	def items(self):
		return self._data.items()

	def index(self, key):
		return self._data.index(key)

	def at(self, index):
		return self._data.at(index)
	
	def key_at(self, index):
		return self._data.key_at(index)

	def value_at(self, index):
		return self._data.value_at(index)
	
	def add(self, value):
		key = self._id
		self._data[key] = value
		self._id += 1
