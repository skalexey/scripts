import os
from pathlib import Path
from test import *


def dirname_test():
	p = "htis/is/a/path"
	d = os.path.dirname(p)
	log(f"Dirname of '{p}': {d}")
	p2 = Path(p)
	d2 = os.path.dirname(p2)
	log(f"Dirname of '{p2}': {d2}")

def test():
	log(title("Dirname Test"))
	dirname_test()
	log(title("End of Dirname Test"))

run()
