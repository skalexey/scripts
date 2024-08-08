
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
	keys_attr = getattr(target, "keys", None)
	if keys_attr is not None:
		for key in keys_attr():
			if key in source:
				target[key] = source[key]
	else: # It is considered as a list
		items_to_update_count = min(len(target), len(source))
		for index in range(items_to_update_count):
			target[index] = source[index]

def add_new(target, source):
	items_attr = getattr(source, "items", None)
	if items_attr is not None:
		for key, value in items_attr():
			if key not in target:
				target[key] = value
	else: # It is considered as a list
		items_to_add_count = max(0, len(source) - len(target))
		if items_to_add_count > 0:
			from_index = len(target)
			for i in range(items_to_add_count):
				index = from_index + i
				target.append(source[index])

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

def exclude(from_, what):
	result = from_.__class__()
	items_attr = getattr(from_, "items", None)
	if items_attr is not None:
		for key, value in items_attr():
			if key not in what:
				result[key] = value
		return result
	values_attr = getattr(from_, "values", None)
	if values_attr is not None:
		for value in values_attr():
			if value not in what:
				result.add(value)
		return result
	return [value for value in from_ if value not in what]

def merge_list_into(what, to):
	for index, value in enumerate(what):
		if index < len(to):
			to[index] = value
		else:
			to.append(value)

def merge_lists(what, to):
	result = list(to)
	merge_list_into(what, result)
	return result
