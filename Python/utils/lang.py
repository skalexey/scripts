def extract_self(bound_method):
	if hasattr(bound_method, '__self__'):
		return bound_method.__self__
	return None
