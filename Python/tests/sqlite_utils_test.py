from test import *

import utils.sqlite


def test_create_or_alter_table_from_dict():
	# Example usage:
	json_data = {
		"name": "John Doe",
		"age": 30,
		"city": "New York"
	}
	primary_keys = ["name"]  # Example primary keys
	utils.sqlite.create_or_alter_table_from_dict(json_data, 'users', 'example.db', primary_keys)

def test():
	log(title("SQLite Test"))
	test_create_or_alter_table_from_dict()
	log(title("End of SQLite Test"))
