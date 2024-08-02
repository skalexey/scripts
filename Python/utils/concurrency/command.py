import concurrent.futures
import threading
from collections import deque

import utils.method
from utils.debug import wrap_debug_lock
from utils.log.logger import Logger
from utils.profile.trackable_callable import TrackableOwnedCallable

log = Logger()


class Command(TrackableOwnedCallable):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.future = concurrent.futures.Future()

	def __call__(self, *args, **kwargs):
		result = super().__call__(*args, **kwargs)
		self.future.set_result(result)


class CommandQueue:
	def __init__(self):
		self._queue = None
		self._lock = wrap_debug_lock(threading.Lock())

	def reset(self):
		if self._queue and len(self._queue) > 1:
			msg_addition = f" and the processing is ongoing" if self._lock.is_locked() else ""
			raise Exception(utils.method.msg_kw(f"queue is not empty{msg_addition}")) # TODO: comment out if not critical
		self._queue = None
		self._lock = wrap_debug_lock(threading.RLock())

	def add_command(self, cb, *args, **kwargs):
		log.debug(utils.method.msg_kw())
		command = Command(cb, args=args, kwargs=kwargs)
		with self._lock:
			if self._queue is None:
				self._queue = deque()
			self._queue.append(command)
		return command.future

	def process_commands(self):
		if self._queue:
			while self._queue:
				with self._lock:
					command = self._queue.popleft()
				log.debug(utils.method.msg_kw(f"Processing command: {command}"))
				command()
