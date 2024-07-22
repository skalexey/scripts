import re


def to_camel_case(snake_str, delimiter=None):
	_delimiter = delimiter or ''
	components = snake_str.split('_')
	return _delimiter.join(x.capitalize() or '_' for x in components)

def to_snake_case(camel_str):
	return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def is_datetime(string):
	pattern = r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2}(\.\d{1,6})?)?(Z|[\+\-]\d{2}:\d{2})?$'
	return bool(re.match(pattern, string))
