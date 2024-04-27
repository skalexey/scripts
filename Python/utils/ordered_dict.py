class OrderedDict:
	def __init__(self):
		self.dict = {}
		self.list = []

	def index(self, key):
		index = self.dict.get(key)
		if index is None:
			return -1
		return index
	def get(self, key, default=None):
		value = self.get(key)
		if value is None:
			return default
		return value
		
	def insert(self, index, key, value):
		if key in self.dict:
			raise KeyError(f"Key '{key}' already exists")
		if index < len(self.list):
			for key, value in self.dict.items():
				if value >= index:
					self.dict[key] += 1
		self.dict[key] = index
		self.list.insert(index, value)

	def add(self, key, value):
		if key not in self.dict:
			self[key] = value
			return True
		return False

	def popitem(self):
		key = self.list.pop()
		index = self.dict.pop(key)
		value = self.list[index]
		return (key, value)

	def pop(self, key):
		index = self.dict[key]
		value = self.list.pop(index)
		del self.dict[key]
		return value

	def keys(self):
		return self.dict.keys()

	def values(self):
		return self.list.copy()

	def items(self):
		return [(key, self[key]) for key in self.dict.keys()]
	
	def clear(self):
		self.dict.clear()
		self.list.clear()

	def copy(self):
		new = OrderedMap()
		new.dict = self.dict.copy()
		new.list = self.list.copy()
		return new

	def update(self, other):
		self.dict.update(other.dict)
		self.list.extend(other.list)

	def setdefault(self, key, default=None):
		if key not in self.dict:
			self[key] = default
		return self[key]
	
	def __setitem__(self, key, value):
		index = self.dict.get(key)
		if index is None:
			index = len(self.list)
			self.list.append(value)
			self.dict[key] = index
		else:
			self.list[index] = value

	def __getitem__(self, key):
		index = self.dict.get(key)
		return self.list[index] if index is not None else None

	def __delitem__(self, key):
		index = self.dict.pop(key)
		del self.list[index]
		for key, value in self.dict.items():
			if value > index:
				self.dict[key] -= 1

	def __iter__(self):
		return iter(self.list)

	def __len__(self):
		return len(self.list)

	def __contains__(self, key):
		return key in self.dict

	def __str__(self):
		return str(self.dict)

	def __repr__(self):
		return repr(self.dict)

	def __eq__(self, other):
		return self.dict == other.dict

	def __ne__(self, other):
		return self.dict != other.dict

	def __lt__(self, other):
		return self.dict < other.dict

	def __le__(self, other):
		return self.dict <= other.dict

	def __gt__(self, other):
		return self.dict > other.dict

	def __ge__(self, other):
		return self.dict >= other.dict

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
		new = OrderedMap()
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
		new = OrderedMap()
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
		return reversed(self.list)
