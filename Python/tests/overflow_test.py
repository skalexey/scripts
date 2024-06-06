import sys
from test import *


def test():
	logger.log(title("Overflow Test begin"))
	int = sys.maxsize * sys.maxsize * sys.maxsize * sys.maxsize
	logger.log(f"sys.maxsize: {int}")
	int += 1
	logger.log(f"sys.maxsize + 1: {int}")
	logger.log(title("Overflow Test end"))

run()