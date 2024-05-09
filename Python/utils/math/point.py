import os
import sys
this_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, this_dir)
from vector import Vector

class Point(Vector):
	def __init__(self):
		self.data = []

	def __repr__(self):
		return f"Point({self.data})"
	