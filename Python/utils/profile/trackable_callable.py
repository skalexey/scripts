import traceback

import utils.memory


def TrackableCallableCls(base_class):
	class TrackableCallable(base_class):
		def __init__(self, *args, **kwargs):
			# Store the callstack for debugging purposes
			self.traceback = traceback.format_stack()
			super().__init__(*args, **kwargs)
	return TrackableCallable

TrackableCallable = TrackableCallableCls(utils.memory.Callable)
TrackableOwnedCallable = TrackableCallableCls(utils.memory.OwnedCallable)
TrackableSmartCallable = TrackableCallableCls(utils.memory.SmartCallable)
