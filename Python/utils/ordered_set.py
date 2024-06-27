import collections
from functools import total_ordering

import utils.function
from utils.serialize.serializable import Serializable


@total_ordering
class OrderedSet(Serializable):
	def __init__(self, keys=None):
		self._keys = keys or []
		self._dict = {key: index for index, key in enumerate(self._keys)}
		super().__init__(assign_attrs=False) # Assign manually, since assigning algorithm uses collection, an can be configured working with OrderedDict

	def _serialize_mapping(self):
		mapping = super()._serialize_mapping()
		mapping.update({
			"keys": "_keys"
		})
		return mapping

	def at(self, index, default=None):
		return self._keys[index] if index < len(self._keys) and index >= 0 else default

	def index(self, key):
		return self._dict.get(key)
	
	def insert(self, index, key):
		if key in self._dict:
			raise KeyError(utils.function.msg(f"Key '{key}' already exists"))
		if index < len(self._keys):
			for k, v in self._dict.items():
				if v >= index:
					self._dict[k] += 1
		self._dict[key] = index
		self._keys.insert(index, key)

	def set_at(self, index, key, value):
		if index < 0 or index >= len(self._keys):
			raise IndexError(utils.function.msg(f"Index out of range({index})"))
		self._keys[index] = key
		self._dict[key] = index

	def add(self, key):
		idx = self.index(key)
		if idx is None:
			idx = len(self._keys)
			self._keys.append(key)
			self._dict[key] = idx
			return True
		return idx

	def update(self, other):
		for key in other:
			self.add(key)

	def copy(self):
		new = OrderedSet()
		new._dict = self._dict.copy()
		new._keys = self._keys.copy()
		return new

	def sort(self, pred):
		self._keys.sort(key=pred)
		for index, key in enumerate(self._keys):
			self._dict[key] = index

	# Returns an index of the key if it exists.
	# If the key is not present in the set, the second argument is returned if provided, otherwise a KeyError is raised.
	def _pop(self, *args):
		if len(args) > 2:
			raise TypeError(f"pop expected at most 1 arguments, got {len(args)}")
		if len(args) == 0:
			if self.empty():
				raise KeyError("Pop from an empty OrderedSet")
			index_to_remove = len(self._keys) - 1
			key_to_remove = self._keys[index_to_remove]
			# self.remove_at(index_to_remove)
			self._keys.pop()
			del self._dict[key_to_remove]
			return key_to_remove, index_to_remove
		default = args[0] if args else None
		len_before = len(self._dict)
		pop_result = self._dict.pop(*args) # Raise KeyError if key is not present and the default value is not provided
		if len_before == len(self._dict):
			return default, pop_result
		index = pop_result
		val = self._keys.pop(index)
		for k, v in self._dict.items():
			if v > index:
				self._dict[k] -= 1
		return val, index

	def pop(self, *args):
		result = self._pop(*args)
		return result[0] if len(args) == 0 else result[1]

	def clear(self):
		self._dict.clear()
		self._keys.clear()

	def __delitem__(self, key):
		return self.remove(key)

	def remove(self, key):
		return self.pop(key)

	def remove_at(self, index):
		key = self._keys[index]
		self.remove(key)
		
	def empty(self):
		return not bool(self)

	def __bool__(self):
		return bool(self._keys)

	def __iter__(self):
		return iter(self._keys)
	
	def __reversed__(self):
		return reversed(self._keys)

	def __len__(self):
		return len(self._keys)

	def __contains__(self, key):
		return key in self._dict

	def __str__(self):
		values_str = ', '.join([f"'{str(key)}'" for key in self._keys])
		return f"[{{{values_str}}}]"

	def __repr__(self):
		return f"utils.OrderedSet({self._keys})"

	def __eq__(self, other):
		if not isinstance(other, OrderedSet):
			return False
		if len(self) != len(other):
			return False
		if self._dict != other._dict:
			return False
		return True

	def __lt__(self, other):
		if isinstance(other, OrderedSet):
			return self._dict < other._dict
		if isinstance(other, list):
			return self._keys < other
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
		for k in other:
			key = k[0] if isinstance(k, tuple) else k
			if key in new:
				del new[key]
		return new
	
	def __isub__(self, other):
		for k in other:
			key = k[0] if isinstance(k, tuple) else k
			if key in self:
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
		# Create using a list comprehension
		other_keys = other.keys() if hasattr(other, 'keys') else other
		new = self.__class__([key for key in self._keys if key in other_keys])
		return new
	
	def __iand__(self, other):
		other_keys = other.keys() if hasattr(other, 'keys') else other
		for key in self._keys:
			if key not in other_keys:
				del self[key]
		return self
	
	def __xor__(self, other):
		new = OrderedSet()
		other_keys = other.keys() if hasattr(other, 'keys') else other
		for key in self._keys:
			if key not in other_keys:
				new.add(key)
		for key in other_keys:
			if key not in self:
				new.add(key)
		return new
	
	def __ixor__(self, other):
		other_keys = other.keys() if hasattr(other, 'keys') else other
		for key in other_keys:
			if key in self:
				del self[key]
			else:
				self.add(key)
		return self
	
# if main 
if __name__ == "__main__":
	from utils.log.logger import Logger
	log = Logger()
	def creation_test():
		log.expr("s1 = OrderedSet()")
		log.expr_and_val("s1")
		log.expr("s2 = OrderedSet(['a', 'b', 'c'])")
		log.expr_and_val("s2")
		log.expr("s3 = OrderedSet({'a', 'b', 'c'})")
		log.expr_and_val("s3")
		log.expr("s4 = OrderedSet(s2)")
		log.expr_and_val("s4")
		log.expr("s5 = OrderedSet(s3)")
		log.expr_and_val("s5")
		
	def test_pop():
		def test1():
			ordered_set = OrderedSet(['a', 'b', 'c'])
			assert ordered_set._pop() == ('c', 2)
			assert ordered_set._pop() == ('b', 1)
			assert ordered_set._pop() == ('a', 0)
			ex = None
			try:
				ordered_set.pop()
			except KeyError as e:
				ex = e
				log.expr_and_val("e")
			assert ex is not None

		def test2():
			os = OrderedSet(['a', 'b', 'c'])
			assert os._pop('a') == ('a', 0)
			assert os._pop('b') == ('b', 0)
			assert os._pop('c') == ('c', 0)
			os = OrderedSet(['a', 'b', 'c'])
			assert os.pop('a') == 0
			assert os.pop('b') == 0
			assert os.pop('c') == 0
			ex = None
			try:
				os.pop('a')
			except KeyError as e:
				ex = e
				log.expr_and_val("e")
			assert ex is not None

		def test3():
			os = OrderedSet(['a', 'b', 'c'])
			assert os.pop('a', 'd') == 0
			assert os.pop('b', 'd') == 0
			assert os.pop('c', 'd') == 0
			assert os.pop('d', 'd') == 'd'
			assert os.pop('e', 'd') == 'd'

			os = OrderedSet(['a', 'b', 'c'])
			assert os._pop('a', 'd') == ('a', 0)
			assert os._pop('b', 'd') == ('b', 0)
			assert os._pop('c', 'd') == ('c', 0)
			assert os._pop('d', 'd') == ('d', 'd')
			assert os._pop('e', 'd') == ('e', 'd')

		test1()
		test2()
		test3()

	def test_sub():
		def test1():
			os1 = OrderedSet(['a', 'b', 'c'])
			os2 = OrderedSet(['a', 'b'])
			assert os1 - os2 == OrderedSet(['c'])
			assert os2 - os1 == OrderedSet()
			assert os1 - OrderedSet() == os1
			assert os1 - OrderedSet(['a', 'b', 'c']) == OrderedSet()
			assert os1 - OrderedSet(['a', 'b']) == OrderedSet(['c'])
			assert os1 - OrderedSet(['a', 'c']) == OrderedSet(['b'])
			assert os1 - OrderedSet(['b', 'c']) == OrderedSet(['a'])
			assert os1 - OrderedSet(['a']) == OrderedSet(['b', 'c'])
			assert os1 - OrderedSet(['b']) == OrderedSet(['a', 'c'])
			assert os1 - OrderedSet(['c']) == OrderedSet(['a', 'b'])

		def test2():
			os1 = OrderedSet(['a', 'b', 'c'])
			os2 = OrderedSet(['a', 'b'])
			os1 -= os2
			assert os1 == OrderedSet(['c'])
			os2 -= os1
			assert os2 == OrderedSet(['a', 'b'])

		test1()
		test2()
	test_pop()
	test_sub()
