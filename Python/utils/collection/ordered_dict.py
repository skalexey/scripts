import collections
from abc import ABC, abstractmethod

import utils.method
from utils.collection.ordered_set import OrderedSet


class OrderedDict(OrderedSet):
	def __init__(self, *args, list=None, keys=None, **kwargs):
		if len(args) == 1:
			arg = args[0]
			if isinstance(arg, (dict, collections.OrderedDict, OrderedDict)):
				keys, list = [], []
				for key, value in arg.items():
					keys.append(key)
					list.append(value)
			else:
				raise ValueError(f"Can't instantiate OrderedDict from '{type(arg).__name__}'")
		elif len(args) == 2:
			keys, list = args
		elif len(args) > 2:
			raise ValueError(f"Expected maximum 2 positional arguments, got {len(args)}")
		super().__init__(keys, **kwargs) # Assign manually, since assigning algorithm uses collection, an can be configured working with OrderedDict
		self._list = list or []

	@classmethod
	def from_dict(cls, dictionary):
		keys = list(dictionary.keys())
		values = list(dictionary.values())
		return cls(keys, values)

	def _serialize_mapping(self):
		mapping = super()._serialize_mapping()
		mapping.update({
			"list": "_list"
		})
		return mapping

	def insert(self, index, key, value):
		super().insert(index, key)
		self._list.insert(index, value)

	def set_at(self, index, key, value):
		super().set_at(index, key)
		self._list[index] = value

	def __setitem__(self, key, value):
		result = super().add(key)
		if result is True:
			self._list.append(value)
		else:
			self._list[result] = value

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
		for key, value in other.items():
			self[key] = value

	def copy(self):
		new = OrderedDict()
		new._dict = self._dict.copy()
		new._list = self._list.copy()
		new._keys = self._keys.copy()
		return new

	def sort(self, by='key', reverse=False, key=None):
		items = list(self.items())
		if key is None:
			if by == 'key':
				items.sort(key=lambda x: x[0], reverse=reverse)
			elif by == 'value':
				items.sort(key=lambda x: x[1], reverse=reverse)
			else:
				raise ValueError(utils.method.msg_kw("Invalid 'by' parameter, must be 'key', 'value', or a custom key function must be provided."))
		else:
			items.sort(key=key, reverse=reverse)
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

	def pop(self, *args):
		len_before = len(self)
		pop_result = super().pop(*args)
		if len_before == len(self):
			assert len(args) == 2
			assert pop_result is args[1]
			return pop_result # Default value
		return self._list.pop(pop_result)

	def values(self):
		return self._list

	def items(self):
		return self.__iter__()

	def keys(self):
		return self._keys

	def dictionary(self):
		result = {}
		for key, value in self.items():
			result[key] = value
		return result

	def clear(self):
		super().clear()
		self._list.clear()

	def get(self, key, default=None):
		idx = self.index(key)
		return self._list[idx] if idx is not None else default

	def __getitem__(self, key):
		if isinstance(key, slice):
			keys = self._keys[key]
			result = OrderedDict()
			for k in keys:
				result[k] = self[k]
			return result
		else:
			idx = self.index(key)
			if idx is None:
				raise KeyError(key)
			return self._list[idx]

	def __iter__(self):
		for key, value in zip(self._keys, self._list):
			yield key, value

	def __reversed__(self):
		for index in range(len(self._list) - 1, -1, -1):
			key = self._keys[index]
			value = self._list[index]
			yield key, value

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		# Contents in the format k->i: v
		contents_str = ", ".join([f"{key}->{index}: {value}" for key, index, value in zip(self._keys, range(len(self._list)), self._list)])
		return f"utils.collection.orderedDict({contents_str})"

	def __eq__(self, other):
		if isinstance(other, list):
			return self._list == other
		elif isinstance(other, (dict, collections.OrderedDict)):
			for key, value in other.items():
				if key not in self or self[key] != value:
					return False
			return True
		if not super().__eq__(other):
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

	def __and__(self, other):
		new = self.__class__()
		for key in self.keys():
			if key in other:
				new.add(key)
		return new
	
	def __xor__(self, other):
		new = self.__class__()
		for key in self:
			if key not in other.keys():
				new[key] = self[key]
		for key in other.keys():
			if key not in self:
				new[key] = other[key]
		return new
	
	def __ixor__(self, other):
		for key in other.keys():
			if key in self:
				del self[key]
			else:
				self[key] = other[key]
		return self
	

class OrderedDictWriteInterface(ABC):
	"""Interface for write operations on an OrderedDict-like object."""

	@abstractmethod
	def __setitem__(self, key, value):
		pass

	@abstractmethod
	def setdefault(self, key, default=None):
		pass

	@abstractmethod
	def update(self, other):
		pass

	@abstractmethod
	def pop(self, *args):
		pass

	@abstractmethod
	def popitem(self):
		pass

	@abstractmethod
	def insert(self, index, key, value):
		pass

	@abstractmethod
	def set_at(self, index, key, value):
		pass

	@abstractmethod
	def add(self, key, value):
		pass

	@abstractmethod
	def clear(self):
		pass

	@abstractmethod
	def sort(self, *args, **kwargs):
		pass

	@abstractmethod
	def __delitem__(self, key):
		pass


class OrderedDictNoLockInterface(ABC):
	"""Interface for operations that don't require locking."""

	@abstractmethod
	def copy(self):
		pass

	@abstractmethod
	def __str__(self):
		pass

	@abstractmethod
	def __repr__(self):
		pass
