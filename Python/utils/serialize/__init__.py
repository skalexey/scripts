from utils.lazy_loader import LazyLoader

loader = LazyLoader()

def __getattr__(name):
	return loader.get(name)
