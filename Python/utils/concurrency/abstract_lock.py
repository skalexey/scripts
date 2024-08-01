from abc import ABC, abstractmethod

from utils.lang import safe_enter


class AbstractLock(ABC):
	@abstractmethod
	def acquire(self, blocking=True, timeout=None) -> bool:
		pass

	@abstractmethod
	def release(self):
		pass

	@abstractmethod
	def acquired(self) -> bool:
		pass

	@abstractmethod
	def locked(self) -> bool:
		pass

	@safe_enter
	def __enter__(self):
		self.acquire()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.acquired():
			self.release()
