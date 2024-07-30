import signal

from utils.subscription import Subscription


class SignalRegistry:
	def __init__(self):
		# Dictionary to hold handlers for each signal
		self.handlers = {}

	def subscribe(self, sig, *args, **kwargs):
		# Add a handler to the list for the specified signal
		subscription = self.handlers.get(sig)
		if subscription is None:
			subscription = Subscription()
			self.handlers[sig] = subscription
			# Set up the central signal handler for this signal
			def handle_signal(signum, frame):
				self.handlers[signum].notify(signum, frame)
			signal.signal(sig, handle_signal)
		subscription.subscribe(*args, **kwargs)

	def unsubscribe(self, sig, *args, **kwargs):
		subscription = self.handlers.get(sig)
		if subscription is not None:
			subscription.unsubscribe(*args, **kwargs)
			if subscription.subscriber_count() == 0:
				signal.signal(sig, signal.SIG_DFL)
				del self.handlers[sig]

registry = SignalRegistry()
