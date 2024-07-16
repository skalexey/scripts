# TODO: Wait for the task utilization after cancelling through a future
import asyncio
import concurrent.futures
import threading
import time
import weakref
from collections import deque

import utils.asyncio_utils as asyncio_utils
import utils.method
from utils.live import verify
from utils.log.logger import Logger
from utils.memory import SmartCallable
from utils.profile.trackable_resource import TrackableResource
from utils.subscription import Subscription

log = Logger()


# This class runs any async function passed to it and returns a future that can be awaited on
class TaskScheduler(TrackableResource):
	instances: list[weakref.ref] = []
	on_update = Subscription()

	class LoopOperator:
		def __init__(self):
			self.thread_id = None

		def is_operating(self):
			return self.thread_id is not None

		def is_operating_in_current_thread(self):
			return self.thread_id == threading.current_thread().name

		def __enter__(self):
			if self.thread_id is not None:
				raise RuntimeError(utils.method.msg_kw("Loop is already operating"))
			if self.loop.is_running():
				raise RuntimeError("Unknown operator is already running the loop")
			self.thread_id = threading.current_thread().name
			return self

		def __call__(self, loop):
			self.loop = loop
			return self

		def __exit__(self, exc_type, exc_value, traceback):
			self.thread_id = None

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.update_interval = kwargs.get("update_interval", 0.1)
		self._tasks = {}
		self._queue = deque()
		self._current_task_info = None
		self._loop = None
		self._lock = threading.RLock()
		self._loop_operator = self.LoopOperator()
		self.on_update = Subscription()
		def on_destroyed(ref):
			TaskScheduler.instances.remove(ref)
		ref = weakref.ref(self, on_destroyed)
		TaskScheduler.instances.append(ref)

	@property
	def loop(self):
		with self._lock:
			if self._loop is None:
				self._loop = asyncio_utils.get_event_loop()
		return self._loop


	class TaskInfo:
		def __init__(self, function, task = None, future=None):
			self.function = function
			self.task = task
			self.future = future or asyncio_utils.get_event_loop().create_future()
			super().__init__()
			# self.future = future or asyncio.Future()

	def schedule_task(self, async_function, max_queue_size=0):
		cb = SmartCallable.bind_if_func(async_function, self)
		with self._lock:
			registered_task_count = self.registered_task_count(cb)
			return self._schedule_task(cb, registered_task_count, max_queue_size)
	
	# Schedule a function to run providing the max_queue_size that is less than the total amount of this function among the tasks in the queue
	def schedule_function(self, async_function, max_queue_size=0):
		cb = SmartCallable.bind_if_func(async_function, self)
		with self._lock:
			registered_function_count = self.registered_task_count(cb)
			return self._schedule_task(cb, registered_function_count, max_queue_size)

	def run_parallel_task(self, async_function):
		raise "Not implemented yet."

	def wait_all_tasks(self):
		if len(self._tasks) == 0:
			log.debug(utils.method.msg_kw("Nothing to wait for"))
			return
		tasks = []
		for task_info in list(self._tasks.values()):
			tasks.append(task_info.task)
		log.debug(utils.method.msg_kw(f"Waiting for {len(tasks)} tasks to finish: {tasks}"))
		async def wait_tasks():
			# Suppresses CancelledError exceptions here, but they will still be originally raised in the coros
			await asyncio.gather(*tasks, return_exceptions=True)
		try:
			if self._loop_operator.is_operating():
				if self._loop_operator.is_operating_in_current_thread():
					raise RuntimeError(utils.method.msg_kw("Called wait_all_tasks() from a running task."))
				log.debug(utils.method.msg_kw("Called wait_all_tasks() from a different thread. Waiting for the tasks to finish in the same loop using asyncio.run_coroutine_threadsafe"))
				futures = []
				for task_info in list(self._tasks.values()):
					futures.append(task_info.future)
				async def wait_tasks():
					last_exception = None
					for future in futures:
						try: # Allow all the tasks to complete
							await future
						except BaseException as e:
							log.error(utils.method.msg_kw(f"Exception occurred while waiting for a task future '{future}': {e}"))
							last_exception = e
				future = asyncio.run_coroutine_threadsafe(wait_tasks(), self.loop)
				result = future.result() # Wait and raise exception if occurred in the end. It will never complete the tasks, but just wait for the owner thread to complete them.
				log.debug(utils.method.msg_kw(f"other thread waiting result: {result}"))
			else:
				with self._loop_operator(self.loop):
					result = self.loop.run_until_complete(wait_tasks())
		except BaseException as e:
			log.error(utils.method.msg_kw(f"Exception occurred while waiting for the tasks: {e}"))
			raise
		return result

	def wait(self, future):
		with self._loop_operator(self.loop):
			return future.get_loop().run_until_complete(future)
	
	def cancel_all_tasks(self):
		self._queue.clear()
		for task_info in list(self._tasks.values()):
			task_info.task.cancel()
		self.wait_all_tasks()

	# Use this method in a loop if your application doesn't have an event loop running
	def update(self, dt):
		log.debug(utils.method.msg_kw())
		# Create the loop from the updating thread if it doesn't exist
		# self.loop
		# Update the tasks
		if len(self._tasks) > 0:
			task_info = next(iter(self._tasks.values()))
			future, task = task_info.future, task_info.task
			async def update_task():
				await asyncio.sleep(self.update_interval)
			cur = time.time()
			cancelled = _check_future_task_cancelled(future, task)
			# verify(not task.cancelled(), "Task is cancelled but it still exists in the tasks list") # The task must be removed from the tasks list in the _on_task_done method
			if task.cancelled():
				log.warning("Task is cancelled but it still exists in the tasks list") # The task must be removed from the tasks list in the _on_task_done method
			with self._loop_operator(self.loop) as o:
				future.get_loop().run_until_complete(update_task())
			if future.done():
				if not future.cancelled():
					ex = future.exception()
					if ex is not None:
						log.error(utils.method.msg_kw(f"Exception occurred while updating the tasks: {ex}"))
						raise ex
			taken_time = time.time() - cur
			self.on_update.notify(taken_time)
			TaskScheduler.on_update.notify(self, taken_time)

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
		log.debug(utils.method.msg_kw())
		# Locked by the caller method
		if 0 <= max_queue_size >= registered_task_count:
			task_info = self._create_task_info(async_function)
			self._queue.append(task_info)
			if self._current_task_info is None:
				return self._run_next()
			else:
				return task_info.future
		# Don't fit by queue size
		log.debug(utils.method.msg_kw(f"Task scheduling has been ignored due to the queue size limit"))
		return None

	def _create_task_info(self, async_function):
		future = self.loop.create_future()
		task_info = self.TaskInfo(async_function, future=future)
		return task_info

	def _run_next(self):
		# assert(self.is_current_thread_loop_owner())
		with self._lock:
			task_info = self._queue.popleft()
			assert task_info.task is None
			self._current_task_info = task_info

			# Define a function to create the task
			def create_task():
				task = self.loop.create_task(task_info.function())
				task_info.task = task
				self._tasks[task] = task_info
				log.debug(utils.method.msg(f"Task {task} has been registered. Total task count: {len(self._tasks)}"))
				assert len(self._tasks) == 1
				task.add_done_callback(self._on_task_done)

				# log.attention(f"Added a new task {task} to the loop")

				future = task_info.future

				def future_done(future):
					_check_future_task_cancelled(future, task)
				
				future.add_done_callback(future_done)
				return future

			# Schedule the task creation in a thread-safe manner
			# loop = self.loop
			# future = asyncio.run_coroutine_threadsafe(create_task(), loop).result()
			future = create_task()
			return future

	def _on_task_done(self, task):
		log.debug(utils.method.msg_kw())
		task_info = self._tasks.pop(task)
		assert task_info == self._current_task_info
		task, future = task_info.task, task_info.future
		try:
			if not _check_future_task_cancelled(future, task):
				if not future.done():
					future.set_result(task.result())
		except Exception as e:
			log.error(f"Exception in _on_task_done: {e}")
			if not future.done():
				future.set_exception(e)
		finally:
			self._current_task_info = None
			if len(self._queue) > 0:
				self._run_next()

def _check_future_task_cancelled(future, task):
	if future.cancelled():
		log.debug(utils.method.msg_kw(f"Future has been cancelled"))
		if not task.cancelled():
			task.cancel()
	elif task.cancelled():
		log.debug(utils.method.msg_kw(f"Task has been cancelled"))
		if not future.done():
			future.cancel()
	else:
		return False
	return True
