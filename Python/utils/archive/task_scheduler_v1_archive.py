# TODO: Wait for the task utilization after cancelling through a future
import asyncio
import concurrent.futures
import threading
import time
import weakref
from collections import deque

import utils.asyncio_utils as asyncio_utils
import utils.function
import utils.method
from utils.debug import wrap_debug_lock
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

	def tasks(self):
		return self._tasks

	def schedule_task(self, async_function, max_queue_size=0, *args, **kwargs):
		cb = SmartCallable.bind_if_func(async_function, self, args=args, kwargs=kwargs)
		with self._lock:
			registered_task_count = self.registered_task_count(cb)
			return self._schedule_task(cb, registered_task_count, max_queue_size)
	
	# Schedule a function to run providing the max_queue_size that is less than the total amount of this function among the tasks in the queue
	def schedule_function(self, async_function, max_queue_size=0, *args, **kwargs):
		cb = SmartCallable.bind_if_func(async_function, self, args=args, kwargs=kwargs)
		with self._lock:
			registered_function_count = self.registered_task_count(cb)
			return self._schedule_task(cb, registered_function_count, max_queue_size)

	def run_parallel_task(self, async_function):
		raise "Not implemented yet."

	def run_until_complete(self, awaitable, on_try_use=None):
		log.debug(utils.method.msg_kw())
		try:
			with self._loop_operator.try_use(self.loop) as operator:
				try_result = operator.try_result()
				if on_try_use is not None:
					on_try_use(try_result)
				if try_result is True:
					log.debug(utils.method.msg_kw(f"Running the task until complete"))
					result = self.loop.run_until_complete(awaitable)
					log.verbose(utils.method.msg_kw(f"run_until_complete result: {result}"))
				else:
					if operator.is_operating_in_current_thread():
						raise RuntimeError(utils.method.msg_kw("Called run_until_complete() from a running task."))
					log.debug(utils.method.msg_kw("Called run_until_complete() from a different thread. Pereforming the task in the same loop using asyncio.run_coroutine_threadsafe"))
					future = asyncio.run_coroutine_threadsafe(awaitable, self.loop)
					result = future.result() # Wait and raise exception if occurred in the end. It will never complete the tasks, but just wait for the owner thread to complete them.
					log.verbose(utils.method.msg_kw(f"other thread run_until_complete result: {result}"))
		except BaseException as e:
			log.error(utils.method.msg_kw(f"Exception occurred while running the awaitable: '{e}'"))
			raise
		return result

	# Returns False in the case of a timeout. Otherwise, always True
	def wait_all_tasks(self, timeout=None):
		if len(self._tasks) == 0:
			log.debug(utils.method.msg_kw("Nothing to wait for"))
			return
		tasks = []
		futures = []
		for task_info in list(self._tasks.values()):
			tasks.append(task_info.task)
			futures.append(task_info.future)
		log.debug(utils.method.msg_kw(f"Waiting for {len(tasks)} tasks to finish: {tasks}"))
		async def wait_tasks():
			await asyncio.gather(*tasks, return_exceptions=True)
			return True
		with self._loop_operator.check_if_free(self.loop) as operator:
			if operator.check_result() is False:
				if operator.is_operating_in_current_thread():
					raise RuntimeError(utils.method.msg_kw("Called wait_all_tasks() from a running task."))
				log.debug(utils.method.msg_kw("Called wait_all_tasks() from a different thread. Waiting for the tasks to finish in the same loop using asyncio.run_coroutine_threadsafe"))
				futures = []
				for task_info in list(self._tasks.values()):
					futures.append(task_info.future)
				async def wait_tasks_through_futures():
					for future in futures:
						try: # Allow all the tasks to complete
							await future
						except BaseException as e:
							log.error(utils.method.msg_kw(f"Exception occurred while waiting for a task future '{future}': '{e}'"))
					return True
				wait_tasks = wait_tasks_through_futures
			else:
				log.debug(utils.method.msg_kw(f"Running {len(tasks)} tasks until complete"))

			def on_try_use(try_result): # TODO: encapsulate if possible
				log.verbose(utils.function.msg_kw("Lock released"))
				operator.enter_lock.release()
				assert operator.enter_lock._is_owned() is False

			try:
				self._wait(wait_tasks(), timeout, on_try_use)
			except asyncio.TimeoutError as e:
				log.info(utils.method.msg_kw(f"Timeout occurred while waiting for all tasks to finish"))
				if operator.check_result():
					log.debug(utils.method.msg_kw("Setting TimeoutError to the future"))
					for future in futures:
						if not future.done():
							future.set_exception(e)
							log.debug("TimeoutError has been set to the future")
					log.debug(utils.method.msg_kw("Cancelling all the tasks"))
					for task in tasks:
						if not task.done():
							task.cancel()
							log.debug("Task has been cancelled")
					log.debug(utils.method.msg_kw("Waiting for the tasks to be cancelled"))
					async def small_update():
						await asyncio.sleep(0)
					try:
						self.loop.run_until_complete(small_update())
					except BaseException as e:
						log.error(utils.method.msg_kw(f"Exception occurred while performing a small update: '{e}'"))
					log.debug(utils.method.msg_kw("All the tasks have been cancelled"))
				else:
					log.debug(utils.method.msg_kw("There is an active operator, so exit without doing nothing"))
				return False
		return True

	# Returns the result of the future in the case of a successful completion
	def wait(self, future):
		verify(self._loop is not None and future.get_loop() == self._loop, utils.method.msg_kw("Foreign future provided"))
		return self._wait(future)

	class WaitForResult:
		def __init__(self):
			self.result = None
			self.timedout = None

	# Returns WaitForResult object that contains the result of the future in the case of a successful completion and a timedout flag
	def wait_for(self, future, timeout):
		result = self.WaitForResult()
		try:
			result.timedout = False
			result.result = self.wait(future, timeout)
		except asyncio.TimeoutError as e:
			log.info(utils.method.msg_kw(f"Timeout occurred while waiting for a future: {e}"))
			result.timedout = True
		return result

	# Raises asyncio.TimeoutError in the case	
	def _wait(self, awaitable, timeout=None, *args, **kwargs):
		if timeout is None:
			_awaitable = awaitable
		else:
			async def wait_with_timeout_and_shield():
				await asyncio.wait_for(asyncio.shield(awaitable), timeout)
			_awaitable = wait_with_timeout_and_shield()
		# awaitable_str = f" a future" if isinstance(_awaitable, asyncio.Future) else f" an awaitable"
		result = self.run_until_complete(_awaitable, *args, **kwargs) # Future's loop must equal to self.loop is this future was created by this TaskScheduler, but if someone decides to pass here a future of another origin, then it does not make sense to execute in this scheduler.
		return result
	
	def cancel_all_tasks(self):
		log.debug(utils.method.msg_kw(f"Cancelling {len(self._tasks)} tasks"))
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
			with self._loop_operator.try_use(self.loop) as operator:
				if operator.try_result() is True:
					self.loop.run_until_complete(update_task())
				# TODO: process exceptions in the current operator
			if future.done():
				if not future.cancelled():
					ex = future.exception()
					if ex is not None:
						log.error(utils.method.msg_kw(f"Exception occurred while updating the tasks: '{ex}'"))
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
					log.debug(utils.function.msg_kw())
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

	class LoopOperator:
		def __init__(self):
			self.thread_id = None
			self.enter_lock = wrap_debug_lock(threading.RLock())

		def is_operating(self):
			return self.thread_id is not None

		def is_operating_in_current_thread(self):
			return self.thread_id == threading.current_thread().name


		class LoopOperatorEnter:
			def __init__(self, loop=None, operator=None, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.loop = loop
				self.operator = operator

			def __getattr__(self, name):
				return getattr(self.operator, name)

			def _loop_is_operating_msg(self):
				return utils.method.msg_kw(f"Loop is already operating by '{self.operator.thread_id}'")

			def _on_is_operating_check(self, is_operating):
				if is_operating:
					msg = self._loop_is_operating_msg()
					raise RuntimeError(msg)
				else:
					self.operator.thread_id = threading.current_thread().name

			def _is_operating(self):
				is_operating = self.operator.is_operating()
				if not is_operating:
					if self.loop.is_running():
						raise RuntimeError("Unknown operator is already running the loop")
				return is_operating

			def __enter__(self):
				with self.operator.enter_lock:
					current_thread_id = threading.current_thread().name
					log.verbose(utils.method.msg_kw(f"Thread '{current_thread_id}' is entering the loop operator"))
					is_operating = self._is_operating()
					self._on_is_operating_check(is_operating)
					log.verbose(utils.method.msg_kw(f"Thread '{current_thread_id}' entered the loop operator"))
					return self
			
			def __exit__(self, exc_type, exc_value, traceback):
				operator_thread_id = self.operator.thread_id
				current_thread_id = threading.current_thread().name
				is_owner = operator_thread_id == current_thread_id
				msg_addition = "" if is_owner else " (not the owner)"
				log.verbose(utils.method.msg_kw(f"Thread '{current_thread_id}'{msg_addition} is exiting the loop operator"))
				if is_owner:
					self.operator.thread_id = None
				log.verbose(utils.method.msg_kw(f"Thread '{current_thread_id}'{msg_addition} exited the loop operator"))


		class LoopOperatorEnterCheckIfFree(LoopOperatorEnter):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self._check_result = None
				self.lock = self.operator.enter_lock # RLock

			def check_result(self):
				return self._check_result

			def _on_is_operating_check(self, is_operating):
				self._check_result = not is_operating

			def __enter__(self):
				log.verbose(utils.method.msg_kw("Trying to acquire the lock"))
				self.lock.acquire() # Unlock in __exit__
				log.verbose(utils.method.msg_kw("Lock acquired"))
				self._check_result = not self._is_operating()
				return self
			
			def __exit__(self, exc_type, exc_value, traceback):
				if self.lock._is_owned():
					log.verbose(utils.method.msg_kw("Releasing the lock"))
					self.lock.release()
					log.verbose(utils.method.msg_kw("Lock released"))


		class LoopOperatorEnterTryUse(LoopOperatorEnter):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self._try_result = None

			def try_result(self):
				return self._try_result

			def _on_is_operating_check(self, is_operating):
				if is_operating:
					log.info(self._loop_is_operating_msg())
				else:
					super()._on_is_operating_check(is_operating)
				self._try_result = not is_operating


		def __call__(self, loop):
			params = self.LoopOperatorEnter(loop=loop, operator=self)
			return params
		
		def try_use(self, loop):
			params = self.LoopOperatorEnterTryUse(loop=loop, operator=self)
			return params
		
		def check_if_free(self, loop):
			params = self.LoopOperatorEnterCheckIfFree(loop=loop, operator=self)
			return params


	class TaskInfo:
		def __init__(self, function, task = None, future=None):
			self.function = function
			self.task = task
			self.future = future or asyncio_utils.get_event_loop().create_future()
			super().__init__()
			# self.future = future or asyncio.Future()


def _check_future_task_cancelled(future, task):
	if future.cancelled():
		log.debug(utils.method.msg_kw(f"Future has been cancelled"))
		if not task.cancelled():
			log.debug(utils.method.msg_kw(f"Cancelling the task"))
			task.cancel()
			log.debug(utils.method.msg_kw(f"Cancelled the task"))
		else:
			log.debug(utils.method.msg_kw(f"Task is already cancelled"))
	elif task.cancelled():
		log.debug(utils.method.msg_kw(f"Task has been cancelled"))
		if not future.done():
			log.debug(utils.method.msg_kw(f"Cancelling the future"))
			future.cancel()
			log.debug(utils.method.msg_kw(f"Cancelled the future"))
		else:
			log.debug(utils.method.msg_kw(f"Future is already done"))
	else:
		return False
	return True
