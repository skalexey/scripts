import inspect
from test import *


def signature_test():
	log(title("Signature Test"))
	def print_function_signature(func):
		# Get the function name
		func_name = func.__name__
		
		# Get the signature
		signature = inspect.signature(func)
		
		# Format and print the function name with its parameters
		log(f"{func_name}{signature}")

	# Example function
	def example_function(param1, param2='default2', param3=42):
		pass

	# Example usage
	print_function_signature(example_function)
	log(title("End of Signature Test"))

def test():
	log(title("Inspect Test"))
	signature_test()
	log(title("End of Inspect Test"))
run()
