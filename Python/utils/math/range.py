import random


class Range:
	def __init__(self, min, max=None):
		self.data = [min, max if max is not None else min]
		super().__init__()
	
	def size(self):
		return abs(self.data[1] - self.data[0])

	def expand(self, _min_, _max_=None):
		self.data[0] = min(_min_, self.min)
		self.data[1] = max(_max_ if _max_ is not None else _min_, self.max)

	def random(self):
		return random.uniform(self.min, self.max)

	@property
	def min(self):
		return self.data[0]

	@property
	def max(self):
		return self.data[1]

	def __contains__(self, item):
		return self.min <= item <= self.max

	def __repr__(self):
		return f"Range({self.min}, {self.max})"
	
	def __getitem__(self, item):
		return self.data[item]