from utils.lang import NoValue


class AttributesView:
	"""
	Allows to access the object's attributes as a dictionary.
	"""
	def __init__(self, obj):
		self._obj = obj

	def _non_dunder_attrs(self):
		for attr_name in dir(self._obj):
			if not attr_name.startswith('__'):
				yield attr_name, getattr(self._obj, attr_name)

	def items(self):
		return iter(self._non_dunder_attrs())

	def values(self):
		return (value for _, value in self._non_dunder_attrs())

	def keys(self):
		return (key for key, _ in self._non_dunder_attrs())

	def __getitem__(self, key):
		if not key.startswith('__'):
			attr = getattr(self._obj, key, NoValue)
			if attr is not NoValue:
				return attr
		raise KeyError(f"'{key}' not found")

	def __contains__(self, key):
		return not key.startswith('__') and hasattr(self._obj, key)

	def __iter__(self):
		return self.keys()

	def __len__(self):
		return sum(1 for _ in self._non_dunder_attrs())

def test():
	# Example usage
	class MyClass:
		def __init__(self):
			self.attr1 = 'value1'
			self.attr2 = 'value2'

		def method(self):
			pass

	obj = MyClass()
	wrapper = AttrView(obj)

	# Using items() method
	for key, value in wrapper.items():
		print(f'{key}: {value}')

	# Using values() method
	for value in wrapper.values():
		print(value)

	# Using keys() method
	for key in wrapper.keys():
		print(key)

	# Using __getitem__ method
	print(wrapper['attr1'])

	# Using __contains__ method
	print('attr1' in wrapper)

	# Using __iter__ method
	for key in wrapper:
		print(key)

	# Using __len__ method
	print(len(wrapper))