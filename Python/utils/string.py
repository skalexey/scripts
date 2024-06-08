import re


def snake_to_camel_case(snake_str):
	components = snake_str.split('_')
	return ''.join(x.capitalize() or '_' for x in components)

def camel_to_snake_case(camel_str):
	return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()