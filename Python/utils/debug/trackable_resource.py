import utils.lang
from utils.log.logger import *

log = Logger()

class TrackableResource:
	def __repr__(self):
		super_repr = super().__repr__()
		return f"{self.__class__.__name__}({super_repr})"

	def __init__(self):
		log.verbose(f"TrackableResource: {self}.__init__()")

	def __del__(self):
		log.verbose(f"TrackableResource: {self}.__del__()")
		# Clear all resources stored in the object's attributes since overriding __del__ method changes the behavior of garbage collection
		utils.lang.clear_resources(self)
