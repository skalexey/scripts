import asyncio
import utils.asyncio
from collections import deque

class FunctionTaskScheduler:
	def __init__(self, *args, **kwargs):
		# Get update_interval from kwargs
		self.update_interval = kwargs.get("update_interval", 0.1)
		self._tasks = {}
		self._functions = {}

	class FunctionInfo:
		def __init__(self, function, future = None):
			self.function = function
			self.future = future
			self.queue = deque()
		
	def schedule_task(self, async_function, max_queue_size = 0):
		future = None
		function_info = self._functions.get(async_function)
		if function_info is not None:
			if not function_info.future.done():
				if not (0 <= max_queue_size > len(function_info.queue)):
					return function_info.future
				future = asyncio.Future()
				function_info.queue.append(future)
				return future
		else:
			function_info = self.FunctionInfo(async_function)
			self._functions[async_function] = function_info
		# The current task is done at this point, so we can enque a new one and run right away
		if 0 <= max_queue_size >= len(function_info.queue):
			function_info.queue.append(asyncio.Future())
			return self._run_next(function_info)
		else:
			# Return the following task to be run
			return function_info.queue[0]

	def get_task_future(self, async_function):
		function_info = self._functions.get(async_function)
		if function_info is None:
			return None
		return function_info.future

	def wait_all_tasks(self):
		for task_data in list(self._tasks.values()):
			future = task_data[0]
			future.get_loop().run_until_complete(future)

	# Use this method in a loop if your application doesn't have an event loop running
	def update(self, dt):
		if len(self._tasks) > 0:
			future = self._tasks[0][0]
			async def update_task():
				await asyncio.sleep(self.update_interval)
			future.get_loop().run_until_complete(update_task())

	def _set_result(self, task):
		future, async_function = self._tasks.pop(task)
		if task.cancelled():
			return
		assert not future.done()
		future.set_result(task.result())
		function_info = self._functions.get(async_function)
		if len(function_info.queue) > 0:
			self._run_next(function_info)

	def _run_next(self, function_info):
		future = function_info.queue.popleft()
		function_info.future = future
		loop = utils.asyncio.get_event_loop()
		task = loop.create_task(function_info.function())
		task.add_done_callback(self._set_result)
		self._tasks[task] = (future, function_info.function)
		def future_done(future):
			if future.cancelled():
				task.cancel()
		future.add_done_callback(future_done)
		return future