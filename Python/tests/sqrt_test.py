import math
import time

def my_sqrt(x):
	return x ** 0.5

def inverse_sqrt(x):
	return x ** -0.5

def test_my_sqrt():
	# Measure the time
	start = time.time()
	# Test the function
	# Just go through a big loop from 1 with incrementing number
	for i in range(1, 1000000):
		my_sqrt(i)
	# Measure the time
	end = time.time()
	# Print the time
	print(f"Time elapsed for my_sqrt: {end - start}")

def test_inverse_sqrt():
	# Measure the time
	import time
	# Measure the time
	start = time.time()
	# Test the function
	# Just go through a big loop with incrementing number
	for i in range(1, 1000000):
		inverse_sqrt(i)
	# Measure the time
	end = time.time()
	# Print the time
	print(f"Time elapsed for inverse_sqrt: {end - start}")

def test_sqrt():
	# Measure the time
	import time
	# Measure the time
	start = time.time()
	# Test the function
	# Just go through a big loop with incrementing number
	for i in range(1, 1000000):
		math.sqrt(i)
	# Measure the time
	end = time.time()
	# Print the time
	print(f"Time elapsed for sqrt: {end - start}")

# Main function
def main():
	# Test the functions
	test_my_sqrt()
	test_inverse_sqrt()
	test_sqrt()
	# Once again
	test_my_sqrt()
	test_inverse_sqrt()
	test_sqrt()

# Entry point of the script
if __name__ == "__main__":
	main()
