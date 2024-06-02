import asyncio
from collections import deque

import utils.asyncio_utils


# This class runs any async function passed to it and returns a future that can be awaited on
class TaskScheduler():
	def __init__(self, *args, **kwargs):
		self.update_interval = kwargs.get("update_interval", 0.1)
		self._tasks = {}
		self._queue = deque()
		self._current_task_info = None

	class TaskInfo:
		def __init__(self, function, task = None, future=asyncio.Future()):
			self.function = function
			self.task = task
			self.future = future

	def schedule_task(self, async_function, max_queue_size=0):
		if 0 <= max_queue_size > len(self._queue) or self._current_task_info is None:
			task_info = self._create_task_info(async_function)
			self._queue.append(task_info)
			if self._current_task_info is None:
				return self._run_next()
		# Don't fit by queue size
		return None

	def wait_all_tasks(self):
		for task_info in list(self._tasks.values()):
			task_info.future.get_loop().run_until_complete(task_info.future)

	def wait(self, future):
		future.get_loop().run_until_complete(future)
	
	# Use this method in a loop if your application doesn't have an event loop running
	def update(self, dt):
		if len(self._tasks) > 0:
			future = self._tasks[0][0]
			async def update_task():
				await asyncio.sleep(self.update_interval)
			future.get_loop().run_until_complete(update_task())

	def _create_task_info(self, async_function):
		task_info = self.TaskInfo(async_function)
		self._tasks[async_function] = task_info
		return task_info

	def _run_next(self):
		task_info = self._queue.popleft()
		self._current_task_info = task_info
		loop = utils.asyncio_utils.get_event_loop()
		task = loop.create_task(task_info.function())
		task_info.task = task
		task.add_done_callback(self._set_result)
		self._tasks[task] = task_info
		future = task_info.future
		def future_done(future):
			if future.cancelled():
				task.cancel()
		future.add_done_callback(future_done)
		return future

	def _set_result(self, task):
		task_info = self._tasks.pop(task)
		task, future = task_info.task, task_info.future
		if task.cancelled():
			return
		# assert not future.done()
		if not future.done():
			future.set_result(task.result())
		if len(self._queue) > 0:
			self._run_next()
		else:
			self._current_task_info = None