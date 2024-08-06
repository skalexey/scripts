from utils.lang import safe_enter


class Atomic:
	def __init__(self, obj, lock):
		object.__setattr__(self, 'obj', obj)
		object.__setattr__(self, 'lock', lock)

	@safe_enter
	def __enter__(self):
		self.lock.acquire()
		return self.obj

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.lock.release()

	def __getattr__(self, name):
		with self.lock:
			return getattr(self.obj, name)

	def __setattr__(self, name, value):
		with self.lock:
			setattr(self.obj, name, value)

	def update(self, new_obj):
		with self.lock:
			self.obj = new_obj
			return new_obj
