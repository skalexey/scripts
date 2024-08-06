from test import *


def generator_test():
	# Create a generator
	gen = (x * x for x in range(10))

	# Use the generator in a for loop
	for val in gen:
		log(val)

	# Re-create the generator because it was exhausted by the for loop
	gen = (x * x for x in range(10))

	# Convert the generator to a list
	lst = list(gen)
	log(lst)

	# Re-create the generator
	gen = (x * x for x in range(10))

	# Calculate the sum of the generator
	total = sum(gen)
	log(total)

	# Re-create the generator
	gen = (x * x for x in range(10))

	# Get the maximum value from the generator
	max_val = max(gen)
	log(max_val)

	# Re-create the generator
	gen = (x * x for x in range(10))

	# Check if any value is greater than 50
	has_any = any(x > 50 for x in gen)
	log(has_any)

	# Re-create the generator
	gen = (x * x for x in range(10))

	# Use with itertools
	import itertools
	cycled = itertools.cycle(gen)
	for _ in range(20):
		log(next(cycled))


def test():
	log(title("Generator Test"))
	generator_test()
	log(title("End of Generator Test"))

run()
