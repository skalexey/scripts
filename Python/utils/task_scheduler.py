# TODO: Wait for the task utilization after cancelling through a future
import asyncio
import threading
from collections import deque
from datetime import datetime

import utils.asyncio_utils
from utils.log.logger import *

log = Logger()


# This class runs any async function passed to it and returns a future that can be awaited on
class TaskScheduler():
	def __init__(self, *args, **kwargs):
		self.update_interval = kwargs.get("update_interval", 0.1)
		self._tasks = {}
		self._queue = deque()
		self._current_task_info = None
		self._loop = None
		self._thread_id = None
		self._lock = threading.RLock()

	@property
	def loop(self):
		with self._lock:
			if self._loop is None:
				self._loop = utils.asyncio_utils.get_event_loop()
				self._thread_id = threading.current_thread().ident
		return self._loop

	class TaskInfo:
		def __init__(self, function, task = None, future=None):
			self.function = function
			self.task = task
			self.future = future or utils.asyncio_utils.get_event_loop().create_future()
			# self.future = future or asyncio.Future()

	def schedule_task(self, async_function, max_queue_size=0):
		with self._lock:
			queue_size = len(self._queue)
			registered_task_count = queue_size + (1 if self._current_task_info is None else 0)
			return self._schedule_task(async_function, registered_task_count, max_queue_size)
	
	# Schedule a function to run providing the max_queue_size that is less than the total amount of this function among the tasks in the queue
	def schedule_function(self, async_function, max_queue_size=0):
		with self._lock:
			enqueued_function_count = self.queue_size(async_function)
			registered_function_count = enqueued_function_count + (1 if self._current_task_info is not None and self._current_task_info.function == async_function else enqueued_function_count)
			return self._schedule_task(async_function, registered_function_count, max_queue_size)

	def run_parallel_task(self, async_function):
		raise "Not implemented yet."

	def wait_all_tasks(self):
		for task_info in list(self._tasks.values()):
			try:
				task_info.future.get_loop().run_until_complete(task_info.future)
			except asyncio.CancelledError:
				log.info(f"Task has been cancelled (tas_info: {task_info})")

	def wait(self, future):
		future.get_loop().run_until_complete(future)
	
	def cancel_all_tasks(self):
		self._queue.clear()
		for task_info in list(self._tasks.values()):
			task_info.task.cancel()

	# Use this method in a loop if your application doesn't have an event loop running
	def update(self, dt):
		# Create the loop from the updating thread if it doesn't exist
		self.loop
		# Update the tasks
		if len(self._tasks) > 0:
			future = next(iter(self._tasks.values())).future
			async def update_task():
				await asyncio.sleep(self.update_interval)
			future.get_loop().run_until_complete(update_task())

	def registered_task_count(self, function=None):
		return self.task_in_work_count(function) + self.queue_size(function)
	
	def queue_size(self, function=None):
		if function is not None:
			return sum(1 for task_info in self._queue if task_info.function == function)
		return len(self._queue)

	def task_in_work_count(self, function=None):
		if function is not None:
			return sum(1 for task_info in self._tasks.values() if task_info.function == function)
		return len(self._tasks)

	def _schedule_task(self, async_function, registered_task_count, max_queue_size=0):
		# Locked by the caller method
		if 0 <= max_queue_size >= registered_task_count:
			task_info = self._create_task_info(async_function)
			self._queue.append(task_info)
			if self._current_task_info is None:
				return self._run_next()
			else:
				return task_info.future
		# Don't fit by queue size
		return None

	def _create_task_info(self, async_function):
		future = self.loop.create_future()
		task_info = self.TaskInfo(async_function, future=future)
		return task_info

	def _run_next(self):
		thread_id = threading.current_thread().ident
		# assert(thread_id == self._thread_id)
		with self._lock:
			task_info = self._queue.popleft()
			assert task_info.task is None
			self._current_task_info = task_info

			# Define a function to create the task
			def create_task():
				task = self.loop.create_task(task_info.function())
				task_info.task = task
				self._tasks[task] = task_info
				assert len(self._tasks) == 1
				task.add_done_callback(self._set_result)

				future = task_info.future

				def future_done(future):
					if future.cancelled():
						task.cancel()

				future.add_done_callback(future_done)
				return future

			# Schedule the task creation in a thread-safe manner
			loop = self.loop
			log.debug("Acquired the loop")
			# future = asyncio.run_coroutine_threadsafe(create_task(), loop).result()
			future = create_task()
			return future

	def _set_result(self, task):
		task_info = self._tasks.pop(task)
		assert task_info == self._current_task_info
		task, future = task_info.task, task_info.future
		if task.cancelled():
			if not future.done():
				future.cancel()
		else:
			if not future.done():
				future.set_result(task.result())
		self._current_task_info = None
		if len(self._queue) > 0:
			self._run_next()
