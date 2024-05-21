import math
import random

class Range:
	def __init__(self, min, max = None):
		self.data = (min, max if max is not None else min)
	
	def size(self):
		return math.abs(self.data[1] - self.data[0])

	def expand(self, min, max = None):
		self.data[0] = min(min, self.min)
		self.data[1] = max(max if max is not None else min, self.max)

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
