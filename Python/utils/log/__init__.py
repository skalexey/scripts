import importlib


def __getattr__(name):
	library = importlib.import_module(f"{__name__}.library")
	if name == '__wrapped__':
		return None
	return getattr(library, name)
