from test import *


def keys_test():
	log(title("Dictionary Keys Test"))
	dictionary = {
		"name": "John Doe",
		"age": 30,
		"city": "New York"
	}
	keys_copy = list(dictionary.keys())
	keys_copy.append("country")
	log(keys_copy)
	keys = dictionary.keys()
	log("Here" if "name" in keys else "Not Here")
	log(title("End of Dictionary Keys Test"))

def construct_test():
	log(title("Dictionary Construct Test"))
	dictionary = {
		"name": "John Doe",
		"age": 30,
		"city": "New York"
	}
	log(dictionary)
	l = [1,2,3]
	d = dict(l)
	log(d)
	log(title("End of Dictionary Construct Test"))

def test():
	log(title("Dictionary Test"))
	keys_test()
	construct_test()
	log(title("End of Dictionary Test"))

run()