import importlib

loader = None

def __getattr__(name):
	library = importlib.import_module(f"{__name__}.library")
	if name == '__wrapped__':
		return None
	attr = getattr(library, name, None)
	if attr is None:
		global loader
		if loader is None:
			from utils.lazy_loader import LazyLoader
			loader = LazyLoader()
		return loader.get(name)
	return attr
