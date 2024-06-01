class OrderedDict:
	def __init__(self):
		self._dict = {}
		self._list = []
		self._keys = []

	def index(self, key):
		index = self._dict.get(key)
		if index is None:
			return -1
		return index
	
	def get(self, key, default=None):
		value = self[key]
		if value is None:
			return default
		return value

	def insert(self, index, key, value):
		if key in self._dict:
			raise KeyError(f"Key '{key}' already exists")
		if index < len(self._list):
			for key, value in self._dict.items():
				if value >= index:
					self._dict[key] += 1
		self._dict[key] = index
		self._list.insert(index, value)
		self._keys.insert(index, key)

	def add(self, key, value):
		if key not in self._dict:
			self[key] = value
			return True
		return False

	def sort(self, pred):
		items = list(self.items())
		items.sort(key = pred)
		self.clear()
		for key, value in items:
			self[key] = value

	def at(self, index):
		return (self._keys[index], self._list[index])
	
	def set_at(self, index, key, value):
		if index < 0 or index >= len(self._list):
			raise IndexError(f"OrderedDict: Index out of range({index})")
		del self._dict[self._keys[index]]
		self._keys[index] = key
		self._list[index] = value
		self._dict[key] = index
		
	def value_at(self, index):
		return self._list[index]

	def key_at(self, index):
		return list(self._dict._keys)[index]

	def popitem(self):
		index = self._dict.pop(key)
		key = self._keys.pop(index)
		value = self._list.pop(index)
		return (key, value)

	def pop(self, key):
		index = self._dict[key]
		value = self._list.pop(index)
		self._keys.pop(index)
		del self._dict[key]
		return value

	def keys(self):
		return self._keys

	def values(self):
		return self._list

	def items(self):
		return zip(self._keys, self._list)
	
	def dictionary(self):
		result = {}
		for key, value in self.items():
			result[key] = value
		return result

	def clear(self):
		self._dict.clear()
		self._list.clear()
		self._keys.clear()

	def copy(self):
		new = OrderedDict()
		new._dict = self._dict.copy()
		new._list = self._list.copy()
		new.keys = self._keys.copy()
		return new

	def update(self, other):
		self._dict.update(other._dict)
		self._list.extend(other._list)
		self._keys.extend(other.keys)

	def setdefault(self, key, default=None):
		if key not in self._dict:
			self[key] = default
		return self[key]
	
	def __setitem__(self, key, value):
		index = self._dict.get(key)
		if index is None:
			index = len(self._list)
			self._list.append(value)
			self._keys.append(key)
			self._dict[key] = index
		else:
			self._list[index] = value

	def __getitem__(self, key):
		index = self._dict.get(key)
		return self._list[index] if index is not None else None

	def __delitem__(self, key):
		index = self._dict.pop(key)
		del self._list[index]
		del self._keys[index]
		for key, value in self._dict.items():
			if value > index:
				self._dict[key] -= 1

	def remove(self, key):
		del self[key]

	def remove_at(self, index):
		key = self._keys[index]
		del self[key]
		
	def __iter__(self):
		for index in range(len(self._list)):
			key = self._keys[index]
			value = self._list[index]
			yield (key, value)

	def __len__(self):
		return len(self._list)

	def __contains__(self, key):
		return key in self._dict

	def __str__(self):
		return str(self._dict)

	def __repr__(self):
		return repr(self._dict)

	def __eq__(self, other):
		return self._dict == other._dict

	def __ne__(self, other):
		return self._dict != other._dict

	def __lt__(self, other):
		return self._dict < other._dict

	def __le__(self, other):
		return self._dict <= other._dict

	def __gt__(self, other):
		return self._dict > other._dict

	def __ge__(self, other):
		return self._dict >= other._dict

	def __add__(self, other):
		new = self.copy()
		new.update(other)
		return new

	def __iadd__(self, other):
		self.update(other)
		return self
	
	def __sub__(self, other):
		new = self.copy()
		for key in other:
			del new[key]
		return new
	
	def __isub__(self, other):
		for key in other:
			del self[key]
		return self
	
	def __or__(self, other):
		new = self.copy()
		new.update(other)
		return new
	
	def __ior__(self, other):
		self.update(other)
		return self
	
	def __and__(self, other):
		new = OrderedDict()
		for key in self:
			if key in other:
				new[key] = self[key]
		return new
	
	def __iand__(self, other):
		for key in self:
			if key not in other:
				del self[key]
		return self
	
	def __xor__(self, other):
		new = OrderedDict()
		for key in self:
			if key not in other:
				new[key] = self[key]
		for key in other:
			if key not in self:
				new[key] = other[key]
		return new
	
	def __ixor__(self, other):
		for key in other:
			if key in self:
				del self[key]
			else:
				self[key] = other[key]
		return self
	
	def __reversed__(self):
		return reversed(self._list)
