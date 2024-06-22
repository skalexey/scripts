
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

def fetch_dict(data, keys=None, ignore=set()):
	_keys = keys or data.keys()
	result = {}
	for key in _keys:
		if key not in ignore:
			if key in data:
				result[key] = data[key]
	return result

def fill_dict(target, source, ignore={}):
	for key in target.keys():
		if key not in ignore:
			target[key] = source[key]

def update_existing(target, source):
	for key in target.keys():
		if key in source:
			target[key] = source[key]

def add_to_set_field(target, key, value):
	current = target.get(key, None)
	if current is None:
		target[key] = value
	else:
		if isinstance(current, set):
			current.add(value)
		else:
			target[key] = {current, value}

def as_set(value):
	if value is None:
		return set()
	if isinstance(value, set):
		return value
	return {value}
