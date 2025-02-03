import gc
import sys
import weakref
from test import *

from utils.memory import SmartCallable
from utils.profile.trackable_resource import TrackableResource


class A(TrackableResource):
	pass

def trackable_resource_test():
	log(title("Trackable Resource Test"))
	initial_resource_count = len(TrackableResource.resources)
	log.debug(f"Initial resource count: {initial_resource_count}")
	assert len(TrackableResource.resources) == initial_resource_count
	wr = None
	def encapsulator():
		nonlocal wr
		a = TrackableResource()
		wr = weakref.ref(a)
		assert len(TrackableResource.resources) == initial_resource_count + 1
		# cb = None
		assert wr() is not None
		a = None
		assert wr() is None
	encapsulator()
	log.debug(f"Resource count after encapsulator: {len(TrackableResource.resources)}")
	while wr() is not None:
		gc.collect()
		sleep(0.01)
		refcount = sys.getrefcount(wr())
		log.debug(f"Refcount: {refcount}")
		referrers = gc.get_referrers(wr())
		log.debug(f"Referrers: {referrers}")
		
	assert len(TrackableResource.resources) == initial_resource_count
	log(title("End of Trackable Resource Test"))

def test():
	trackable_resource_test()

run()
