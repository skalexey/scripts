import itertools


class A:
	pass


element = A()
dictionary = {'a': 2, 'b': 3, 'c': 4}

# Combine the single element with the dictionary values
combined_iter = itertools.chain([element], dictionary.values())

# Iterate over the combined iterator
for item in combined_iter:
	print(item)
