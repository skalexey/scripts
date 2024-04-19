from abc import ABC

class Entity(ABC):
	def Is(self, type):
		return isinstance(self, type)
