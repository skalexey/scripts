import concurrent.futures
import signal
import sys
import threading
from abc import ABC
from collections import deque
from datetime import datetime

import utils.debug.debug_detector
from utils.collection.associative_list import AssociativeList
from utils.concurrency.safe_proxy import SafeProxy
from utils.debug import wrap_debug_lock
from utils.lang import safe_super
from utils.log.logger import Logger
from utils.signal_registry import registry as signal_registry
from utils.subscription import Subscription

log = Logger()

class Application(ABC):
	def __init__(self, context, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.context = context
		self.update_thread = None
		self.update_interval = 1 / 60  # 60 FPS
		self.dt_limit = sys.maxsize # TODO: Tests. Move to settings. Remove from Live config
		self._last_time = None
		self._time_lock = wrap_debug_lock(threading.RLock())
		self.on_time_invalidated = Subscription()
		self._on_update_jobs = SafeProxy(AssociativeList(), threading.RLock())
		self._main_thread_job_queue = SafeProxy(deque(), threading.RLock())
		# Define a custom signal handler function to gracefully exit the application
		def signal_handler(sig, frame):
			log(f"Received signal {sig}. Exiting the application.")
			self.stop()
		# Install the signal handler for SIGINT (Ctrl+C)
		signal_registry.subscribe(signal.SIGINT, signal_handler)
		signal_registry.subscribe(signal.SIGTERM, signal_handler)

	def stop(self):
		self.stop_update_loop()
		utils.subscriptions.on_exit.set()
		safe_super(Application, self).stop()

	def run_update_loop(self):
		self.is_update_running = True

		def job():
			while self.is_update_running:
				self.update()

		thread = threading.Thread(target=job)
		thread.start()
		self.update_thread = thread
	
	def stop_update_loop(self):
		self.is_update_running = False
		if self.update_thread is not None:
			self.update_thread.join()

	@property
	def last_time(self):
		with self._time_lock:
			return self._last_time

	@last_time.setter
	def last_time(self, value):
		with self._time_lock:
			self._last_time = value
			if value is None:
				log.debug(utils.method.msg_kw("Time has been invalidated"))
				self.on_time_invalidated()

	def do_in_main_thread(self, func, *args, **kwargs):
		main_thread = threading.main_thread()
		if threading.current_thread() == main_thread:
			return func()
		future = concurrent.futures.Future()
		def job():
			result = func(*args, **kwargs)
			future.set_result(result)
		self._main_thread_job_queue.append(job)
		return future

	def _process_main_thread_jobs(self):
		if not self._main_thread_job_queue:
			return False
		while self._main_thread_job_queue:
			job = self._main_thread_job_queue.popleft() # Performed under the lock through SafeProxy
			job()
		return True

	def _process_update_jobs(self, dt):
		# Process update jobs
		if not self._on_update_jobs:
			return False
		jobs_to_delete = []
		for i in range(len(self._on_update_jobs)):
			id, job = self._on_update_jobs.at(i)
			if job(dt) is False:
				jobs_to_delete.append(id)
		for id, job in self._on_update_jobs:
			if job(dt) is False:
				jobs_to_delete.append(id)
		for id in jobs_to_delete:
			self._on_update_jobs.remove(id)
		return True

	def add_on_update(self, func):
		self._on_update_jobs.add(func)

	def on_update(self, dt):
		self.context.module_manager.call_on_modules("on_update", dt=dt)

	def update(self):
		current_time = self.context.current_time()
		dt = min(current_time - (self.last_time or current_time), self.dt_limit)
		self._process_main_thread_jobs()
		self._process_update_jobs(dt)
		self.last_time = current_time
		self.on_update(dt)

	def check_debug_timespan(self):
		debug_timespan = utils.debug.debug_detector.debug_timespan(self)
		if debug_timespan != 0:
			log.debug(utils.method.msg_kw(f"Debug timespan: {debug_timespan}"))
			self.last_time = None
			return True
		return False

	def current_datetime(self):
		self.check_debug_timespan()
		return datetime.now()
