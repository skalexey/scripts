import asyncio
import utils.asyncio
from collections import deque

# This class runs any async function passed to it and returns a future that can be awaited on
class TaskScheduler:
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

class CommonTaskScheduler(TaskScheduler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		del self._functions
		self._queue = deque()
		self._current_task_info = None

	class TaskInfo:
		def __init__(self, function, task = None, future = asyncio.Future()):
			self.function = function
			self.task = task
			self.future = future

	def _create_task_info(self, async_function):
		task_info = self.TaskInfo(async_function)
		self._tasks[async_function] = task_info
		return task_info

	# def schedule_task(self, async_function, max_queue_size = 0):
	# 	task_info = self._tasks.get(async_function)
	# 	if self._current_task_info is not None:
	# 		if not self._current_task_info.future.done():
	# 			if not (0 <= max_queue_size > len(self._queue)):
	# 				if task_info is self._current_task_info:
	# 					return task_info.future
	# 				else:
	# 					# Don't fit by queue size
	# 					return None
	# 			task_info = self._create_task_info(async_function)
	# 			self._queue.append(task_info)
	# 			return task_info.future
	# 	else:
	# 		task_info = self._create_task_info(async_function)
	# 	# The current task is done at this point, so we can enque a new one and run right away
	# 	if 0 <= max_queue_size >= len(self._queue):
	# 		self._queue.append(task_info)
	# 		return self._run_next()
	# 	# Don't fit by queue size
	# 	return None

	def schedule_task(self, async_function, max_queue_size = 0):
		if 0 <= max_queue_size >= len(self._queue):
			task_info = self._create_task_info(async_function)
			self._queue.append(task_info)
			if self._current_task_info is None:
				return self._run_next()
		# Don't fit by queue size
		return None

	def _run_next(self):
		task_info = self._queue.popleft()
		self._current_task_info = task_info
		loop = utils.asyncio.get_event_loop()
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