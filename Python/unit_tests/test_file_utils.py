import pathlib

import pytest

# Assuming these functions are defined elsewhere and imported
from utils.file import is_open
from utils.path.universal_path import UniversalPath, is_cyg_path, system_path

from tests.test import *


@pytest.fixture
def example_file(tmp_path):
	"""Fixture to create and clean up example.txt."""
	fpath = tmp_path / "example.txt"
	yield fpath
	if fpath.exists():
		fpath.unlink()

@pytest.fixture
def non_existing_file(tmp_path):
	"""Fixture for a non-existing file path."""
	return tmp_path / "not_existing_file.txt"

def test_opened_file(example_file):
	"""Test to check if a file is properly detected as open or closed."""
	log(title("Opened File Test"))

	fpath = example_file
	log(f"Writing to file '{fpath}'")

	with open(fpath, "a+") as f:
		f.write("Writing to a file")
		assert is_open(str(fpath)), f"The file '{fpath}' should be opened for writing."

	assert not is_open(str(fpath)), f"The file '{fpath}' should be closed."
	log.success("End of Opened File Test")

def test_not_existing_file(non_existing_file):
	"""Test to check behavior for non-existing files."""
	log(title("Not Existing File Test"))

	fpath = non_existing_file
	assert not is_open(str(fpath)), f"The file '{fpath}' should not exist nor be opened."
	log.success("End of Not Existing File Test")

def test_is_cyg_path():
	"""Test to verify cygwin-style path detection."""
	log(title("Start of Is Cyg Path Test"))

	assert is_cyg_path("/c/Users/..."), "The path is like '/c/Users/...'."
	assert not is_cyg_path("/mnt/"), "The path is not like '/mnt/'."
	assert not is_cyg_path("c/Users/..."), "The path is not like 'c/Users/...'."
	log.success(title("End of Is Cyg Path Test"))

# def test_convert_cyg_path():
# 	"""Test to verify cygwin-style path conversion."""
# 	log(title("Start of Convert Cyg Path Test"))

# 	assert system_path("/c/Users/...") == "C:\\Users\\...", "The path was expected to be converted to 'C:\\Users\\...'."
# 	assert system_path("/mnt/") == "/mnt/", "The path is not converted."

# 	log.success(title("End of Convert Cyg Path Test"))

def test_convert_cyg_path2():
	"""Test to verify cygwin-style path conversion."""
	log(title("Start of Convert Cyg Path Test"))
	syspath = system_path("/c/Users/skoro/AppData/Roaming/Code/User/settings.json")
	assert syspath == "C:\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json", "The path was expected to be converted to 'C:\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json'."

	log.success(title("End of Convert Cyg Path Test"))

def test_convert_cyg_path3():
	"""Test to verify cygwin-style relative path from root conversion."""
	log(title("Start of Convert Cyg Path Test"))
	syspath = system_path("c/Users/skoro/AppData/Roaming/Code/User/settings.json")
	assert syspath == "c\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json", "The path was expected to be converted to 'c\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json'."

	log.success(title("End of Convert Cyg Path Test"))

def test_path():
	path = "c/Users/skoro/AppData/Roaming/Code/User/settings.json"
	assert str(pathlib.Path(path).resolve()) == "C:\\Users\\skoro\\Scripts\\c\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json", "The path was expected to be converted to 'C:\\Users\\skoro\\Scripts\\c\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json'."

def test_universal_path():
	"""Test to verify the UniversalPath class."""
	log(title("Start of Universal Path Test"))

	path = UniversalPath("/c/Users/skoro/AppData/Roaming/Code/User/settings.json")
	assert str(path) == "C:\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json", "The path was expected to be converted to 'C:\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json'."
	path = UniversalPath("c/Users/skoro/AppData/Roaming/Code/User/settings.json")
	assert str(path) == "c\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json", "The path was expected to be converted to 'c\\Users\\skoro\\AppData\\Roaming\\Code\\User\\settings.json'."

	log.success(title("End of Universal Path Test"))

# To run all tests, simply execute `pytest` in the terminal.

if __name__ == "__main__":
	pytest.main(args=["-s", __file__])
