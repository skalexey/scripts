
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