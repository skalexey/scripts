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
		attr = getattr(self.obj, name)
		if callable(attr):
			# Wrap the method to acquire the lock
			def wrapped(*args, **kwargs):
				with self.lock:
					return attr(*args, **kwargs)
			return wrapped
		return attr
		
	def __setattr__(self, name, value):
		with self.lock:
			setattr(self.obj, name, value)

	# Non-blocking reads
	def __len__(self):
		return len(self.obj)

	def __getitem__(self, key):
		return self.obj[key]

	# Additional interface
	def update(self, new_obj):
		with self.lock:
			self.obj = new_obj
			return new_obj
