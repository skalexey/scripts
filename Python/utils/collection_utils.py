
import sys

if sys.version_info[0] >= 3:
	def find_first(iterable, condition):
		return next(filter(condition, iterable), None)
else:
	# Python 2
	import itertools

	def find_first(iterable, condition):
		return next(itertools.ifilter(condition, iterable), None)

# Universal approach:
# def find_first(iterable, condition):
# 	return next((x for x in iterable if condition(x)), None)

def fetch_dict(data, keys=None, ignore=[]):
	_keys = keys or data.keys()
	return {key: data[key] for key in _keys if key in data and key not in ignore}

def fill_dict(target, source, ignore=[]):
	for key in target.keys():
		if key not in ignore:
			target[key] = source[key]
