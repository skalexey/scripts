from functools import total_ordering

import utils.method


@total_ordering
class Buffer:
	def __init__(self, data=None, offset=None):
		self.set_data(data, offset)

	def set_data(self, data, offset=None):
		self._data = data
		if data is not None:
			view = memoryview(self._data)
			self._view = view[offset:] if offset is not None else view
		else:
			self._view = None

	def read(self, size):
		if size < 0:
			raise ValueError(utils.method.msg_kw("Size must be greater than 0"))
		available = len(self._view)
		data_size_to_read = min(size, available)
		data = self._view[:data_size_to_read]
		self._view = self._view[data_size_to_read:]
		return data

	def __len__(self):
		return len(self._view)

	def __bool__(self):
		return bool(self._view)

	def __getitem__(self, item):
		return self._view[item]

	def __setitem__(self, key, value):
		self._view[key] = value

	def __iter__(self):
		return iter(self._view)

	def __next__(self):
		return next(self._view)

	def __str__(self):
		return str(self._view)

	def __repr__(self):
		return repr(self._view)

	def __bytes__(self):
		return bytes(self._view)

	def __eq__(self, other):
		return self._view == other

	def __lt__(self, other):
		return self._view < other

	def __hash__(self):
		return hash(self._view)

	def __contains__(self, item):
		return item in self._view
	