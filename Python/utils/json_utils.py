import collections
import json
import re


def is_primitive(value):
	return isinstance(value, (int, str, bool, float, type(None)))

def is_serializable(value):
	return is_primitive(value) or isinstance(value, (list, dict, collections.OrderedDict))

# Load with pre-check to avoid capturing raised exceptions
# TODO: optimize-out pattern check for release environment
def load(string):
	if __debug__:
		pattern = r'^\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*$'
		if not re.match(pattern, string):
			return None
	try:
		return json.loads(string)
	except json.JSONDecodeError:
		return None
