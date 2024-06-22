import collections
from functools import total_ordering

from utils.serialize import Serializable


@total_ordering
class OrderedDict(Serializable):
	def __init__(self, list=None, keys=None):
		self._list = list or []
		self._keys = keys or []
		self._dict = {key: index for index, key in enumerate(self._keys)}
		super().__init__(assign_attrs=False) # Assign manually, since assigning algorithm uses collection, an can be configured with OrderedDict

	def _serialize_mapping(self):
		mapping = super()._serialize_mapping()
		mapping.update({
			"list": "_list",
			"keys": "_keys"
		})
		return mapping

	def index(self, key):
		index = self._dict.get(key)
		if index is None:
			return -1
		return index
	
	def insert(self, index, key, value):
		if key in self._dict:
			raise KeyError(f"Key '{key}' already exists")
		if index < len(self._list):
			for k, v in self._dict.items():
				if v >= index:
					self._dict[k] += 1
		self._dict[key] = index
		self._list.insert(index, value)
		self._keys.insert(index, key)

	def set_at(self, index, key, value):
		if index < 0 or index >= len(self._list):
			raise IndexError(f"OrderedDict: Index out of range({index})")
		self._keys[index] = key
		self._list[index] = value
		self._dict[key] = index

	def __setitem__(self, key, value):
		index = self._dict.get(key)
		if index is None:
			index = len(self._list)
			self._list.append(value)
			self._keys.append(key)
			self._dict[key] = index
		else:
			self._list[index] = value

	def add(self, key, value):
		if key not in self._dict:
			self[key] = value
			return True
		return False

	def setdefault(self, key, default=None):
		if key not in self._dict:
			self[key] = default
		return self[key]

	def update(self, other):
		if isinstance(other, OrderedDict):
			self._dict.update(other._dict)
			self._list.extend(other._list)
			self._keys.extend(other.keys)
		elif isinstance(other, (dict, collections.OrderedDict)):
			for key, value in other.items():
				self[key] = value
		else:
			for key, value in other:
				self[key] = value

	def copy(self):
		new = OrderedDict()
		new._dict = self._dict.copy()
		new._list = self._list.copy()
		new._keys = self._keys.copy()
		return new

	def sort(self, pred):
		items = list(self.items())
		items.sort(key=pred)
		self.clear()
		for key, value in items:
			self[key] = value

	def at(self, index):
		return (self._keys[index], self._list[index])
	
	def value_at(self, index):
		return self._list[index]

	def key_at(self, index):
		return self._keys[index]

	def popitem(self):
		key = self._keys.pop()
		value = self._list.pop()
		del self._dict[key]
		return key, value

	def pop(self, key, default=None):
		index = self._dict.get(key)
		if index is None:
			return default
		del self._keys[index]
		del self._dict[key]
		value = self._list.pop(index)
		for key, value in self._dict.items():
			if value > index:
				self._dict[key] -= 1
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

	def get(self, key, default=None):
		index = self._dict.get(key)
		return self._list[index] if index is not None else default

	def __getitem__(self, key):
		if isinstance(key, slice):
			keys = self._keys[key]
			return [self.__getitem__(k) for k in keys]
		else:
			index = self._dict[key]
			return self._list[index]

	def __delitem__(self, key):
		self.pop(key)

	def remove(self, key):
		del self[key]

	def remove_at(self, index):
		key = self._keys[index]
		del self[key]
		
	def __iter__(self):
		for index in range(len(self._list)):
			key = self._keys[index]
			value = self._list[index]
			yield key, value

	def __len__(self):
		return len(self._list)

	def __contains__(self, key):
		return key in self._dict

	def __str__(self):
		return str(self._dict)

	def __repr__(self):
		return f"utils.OrderedDict({self._dict})"

	def __eq__(self, other):
		if not isinstance(other, OrderedDict):
			return False
		if len(self) != len(other):
			return False
		if self._dict != other._dict:
			return False
		if self._list != other._list:
			return False
		return True

	def __lt__(self, other):
		if isinstance(other, OrderedDict):
			return self._dict < other._dict
		if isinstance(other, list):
			return self._list < other
		# It will raise a builtin exception
		return self._dict < other

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
