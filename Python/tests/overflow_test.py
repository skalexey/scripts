import sys
from test import *


def test():
	log(title("Overflow Test begin"))
	int = sys.maxsize * sys.maxsize * sys.maxsize * sys.maxsize
	log(f"sys.maxsize: {int}")
	int += 1
	log(f"sys.maxsize + 1: {int}")
	log(title("Overflow Test end"))

run()