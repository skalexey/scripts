import re


def snake_to_camel_case(snake_str):
	components = snake_str.split('_')
	return ''.join(x.capitalize() or '_' for x in components)

def camel_to_snake_case(camel_str):
	return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

def title(string, filler='=', length=80):
	# Generate a line of the given length with string in the middle separated by spaces from the filler on the sides
	# Example: title("Hello", "=", 80) -> "================================== Hello =================================="
	# Example: title("Hello", "-", 80) -> "---------------------------------- Hello ---------------------------------"
	# Example: title("Hello", "=", 20) -> "======== Hello ========"
	left_length = (length - len(string) - 2) // 2
	right_length = length - len(string) - 2 - left_length
	return f"{filler * left_length} {string} {filler * right_length}"
