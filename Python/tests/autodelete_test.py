import weakref


class AutoDeleteDict:
	def __init__(self):
		self._data = {}

	def __getitem__(self, key):
		value_ref = self._data[key]
		value = value_ref()
		if value is None:
			# If the weak reference is dead, it has already been cleaned up
			raise KeyError(f"Key '{key}' not found")
		return value

	def __setitem__(self, key, value):
		# Store a weak reference to the value with a callback for cleanup
		self._data[key] = weakref.ref(value, self._make_cleanup_callback(key))

	def __delitem__(self, key):
		del self._data[key]

	def __len__(self):
		return len(self._data)

	def __iter__(self):
		return iter(self._data)

	def items(self):
		for key, value_ref in self._data.items():
			value = value_ref()
			if value is not None:
				yield key, value

	def _make_cleanup_callback(self, key):
		def _delete_if_dead(weakref_obj):
			# Remove the entry from the dictionary
			if key in self._data and self._data[key] is weakref_obj:
				del self._data[key]
		return _delete_if_dead

# Example usage:
class WeekObject:
	def __init__(self, data):
		self.data = data

	def __repr__(self):
		return f"WeekObject({self.data})"

# Create AutoDeleteDict instance
auto_delete_dict = AutoDeleteDict()

# Add entries
obj1 = WeekObject("Object 1")
obj2 = WeekObject("Object 2")
auto_delete_dict["key1"] = obj1
auto_delete_dict["key2"] = obj2

# Check length before deletion
print(len(auto_delete_dict))  # Output: 2

# Delete obj1
del obj1

# The entry for obj1 should be automatically removed
print(len(auto_delete_dict))  # Output: 1

# Accessing obj1's key will raise KeyError
try:
	print(auto_delete_dict["key1"])
except KeyError:
	print("Key 'key1' not found and has been removed")

# Verify the dictionary
print(list(auto_delete_dict.items()))  # Output: [('key2', WeekObject(Object 2))]
