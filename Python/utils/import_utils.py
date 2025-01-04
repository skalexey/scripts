import importlib
import inspect
import os
import sys
import threading

import utils.class_utils as class_utils
import utils.function
import utils.log.logger
from utils.debug import wrap_debug_lock
from utils.profile.profiler import TimeProfiler

profiler = TimeProfiler()

log = utils.log.logger.Logger()

_module_cache = None
_cache_lock = wrap_debug_lock(threading.Lock())

_cache_is_loading = None


def module_cache():
	"""
	Finds all the modules in the Python module search path and stores their paths.
	Used by is_module_path() to distinguish module paths from class paths.
	Works asynchronously as this task is quite demanding for big projects.
	"""
	if _module_cache is None:
		with _cache_lock:
			global _cache_is_loading
			if _cache_is_loading is not None:
				return None
			log.debug("Building module cache")
			def work():
				global _module_cache
				global _cache_is_loading
				profiler.start()
				cache = {}
				search_dirs = collect_search_paths()
				for dir_path in search_dirs:
					for root, dirs, files in os.walk(dir_path):
						dirname = os.path.basename(root)
						if dirname.startswith('.'):
							continue
						if dirname == '__pycache__':
							continue
						if '__init__.py' not in files:
							continue
						files.remove('__init__.py')
						for file in files:
							if file.endswith('.py'):
								full_fpath = os.path.join(root, file)
								relpath = os.path.relpath(full_fpath, dir_path)
								module_path = os.path.splitext(relpath)[0].replace(os.path.sep, '.')
								# log.debug(f"Found module: {module_path} in dir_path: '{dir_path}', root: '{root}', file: '{file}'")
								assert module_path not in cache
								cache[module_path] = full_fpath
				log.debug(f"module_cache(): Found {len(cache)} modules in {profiler.measure().timespan} seconds")
				_module_cache = cache
				_cache_is_loading = False
			# Run task in parallel
			_cache_is_loading = True
			threading.Thread(target=work).start()
			
	return _module_cache

def is_module_path(path):
	"""
	Checks if the given path corresponds to an existing Python module.
	Helps distinguish module paths from class paths.
	"""
	cache = module_cache()
	if cache is None: # Cache not ready yet
		log.debug(utils.function.msg(f"Cache not ready yet. Working using find_spec()"))
		try:
			spec = importlib.util.find_spec(path)
			return spec is not None
		except ImportError:
			return False
	return path in cache

def collect_search_paths():
	"""
	Returns a set of all the paths where Python searches for modules.
	"""
	# Start with the system paths
	# Put real paths in a set to avoid duplicates
	paths = set(os.path.realpath(path) for path in sys.path)
	
	# Add the current working directory
	cwd =  os.path.realpath(os.getcwd())
	paths.add(cwd)
	
	# Add site packages directories (if available)
	try:
		from distutils.sysconfig import get_python_lib
		site_packages = os.path.realpath(get_python_lib())
		paths.add(site_packages)
	except ImportError:
		pass  # Handle the case where distutils is not available

	# # Add the directory of the script (if running as a script)
	# script_dir = os.path.dirname(os.path.abspath(__file__))
	# if script_dir not in paths:
	# 	paths.add(script_dir)
	
	return paths

def find_or_import_class(class_path): # e.g. 'module.submodule.ClassName'
	"""
	Searches for a class by its fully qualified path (e.g., 'module.submodule.ClassName') among imported modules, imports if not found, and then returns it.
	"""
	# Try to find the class in globals()
	cls = class_utils.find_class(class_path)
	if cls:
		return cls

	# If not found in globals(), attempt to import the module and retrieve the class
	module_path, class_name = class_path.rsplit('.', 1)
	i = 1
	while True:
		split_result = class_path.rsplit('.', i)
		if len(split_result) < i:
			break
		module_path, class_name = split_result[0:2]
		if module_path in sys.modules:
			module = sys.modules[module_path]
		else:
			if not is_module_path(module_path):
				i += 1
				continue
			module = importlib.import_module(module_path)
		where = module
		for i in range(1, len(split_result)):
			class_name = split_result[i]
			cls = getattr(where, class_name, None)
			if not inspect.isclass(cls):
				raise ValueError(utils.function.msg(f"Expected class, got {cls}"))
			if cls is None:
				return None
			where = cls
		return cls
	raise ValueError(utils.function.msg(f"Couldn't find class '{class_path}' nor import it"))
