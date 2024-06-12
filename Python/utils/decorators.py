def no_return(func):
	def wrapper(*args, **kwargs):
		result = func(*args, **kwargs)
		if result is not None:
			raise ValueError("Function is expected to return None")
		return result
	return wrapper