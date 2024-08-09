from utils.collection.ordered_dict import OrderedDict


class AssociativeList():
	def __init__(self):
		self._data = OrderedDict()
		self._id = 0

	# Redirect all same interface calls to the underlying data object
	def __getattr__(self, name):
		return getattr(self._data, name)

	def __getitem__(self, kay):
		return self._data.at(key)
	
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

	def add(self, value):
		key = self._id
		self._data[key] = value
		self._id += 1
		return key

	def __bool__(self):
		return bool(self._data)
