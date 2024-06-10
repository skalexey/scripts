def extract_self(bound_method):
	if hasattr(bound_method, '__self__'):
		return bound_method.__self__
	return None

def clear_resources(obj):
	for attr in obj.__dict__:
		obj.__dict__[attr] = None
