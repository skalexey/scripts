import os
from test import *


def dir_test():
	# Create a directory
	dirname = "Test_Dir"
	if not os.path.exists(dirname):
		os.mkdir(dirname)

	log.debug(utils.function.msg(f"Directory: {dirname}"))
	# Check if it exists in lower and upper case
	log.expr_and_val("os.path.exists(dirname)")
	log.expr_and_val("os.path.exists(dirname.lower())")
	log.expr_and_val("os.path.exists(dirname.upper())")

	log.expr_and_val("os.path.abspath(dirname)")
	log.expr_and_val("os.path.abspath(dirname.lower())")
	log.expr_and_val("os.path.abspath(dirname.upper())")

	log.expr_and_val("os.path.realpath(dirname)")
	log.expr_and_val("os.path.realpath(dirname.lower())")
	log.expr_and_val("os.path.realpath(dirname.upper())")

def test():
	log(title("Dir Test"))
	dir_test()
	log(title("End of Dir Test"))

run()
