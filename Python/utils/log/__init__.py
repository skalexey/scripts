import importlib


def __getattr__(name):
	library = importlib.import_module(f"{__name__}.library")
	return getattr(library, name)
