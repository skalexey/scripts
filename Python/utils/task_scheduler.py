import asyncio
import concurrent.futures
import threading
import time
import weakref
from collections import deque

import utils.asyncio_utils as asyncio_utils
import utils.function
import utils.method
from utils.concurrency.thread_guard import (
    ThreadGuard,
    allow_any_thread,
    allow_any_thread_with_lock,
)
from utils.debug import wrap_debug_lock
from utils.lang import safe_enter
from utils.live import verify
from utils.log.logger import Logger
from utils.memory import SmartCallable
from utils.profile.trackable_resource import TrackableResource
from utils.subscription import OneTimeSubscription, Subscription

log = Logger()


# This class runs any async function passed to it and returns a future that can be awaited on
class TaskScheduler(TrackableResource, ThreadGuard):
	instances: list[weakref.ref] = []
	on_update = Subscription()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.update_interval = kwargs.get("update_interval", 0.1)
		self._tasks = {}
		self._queue = deque()
		self._current_task_info = None
		self._loop = None
		self._lock = wrap_debug_lock(threading.RLock())
		self._loop_operator = self.LoopOperator()
		self.on_update = Subscription()
		def on_destroyed(ref):
			TaskScheduler.instances.remove(ref)
		ref = weakref.ref(self, on_destroyed)
		TaskScheduler.instances.append(ref)

	@property
	@allow_any_thread
	def loop(self):
		with self._lock:
			if self._loop is None:
				self._loop = asyncio_utils.get_event_loop()
		return self._loop

	def tasks(self):
		return self._tasks

	@allow_any_thread
	def schedule_task(self, async_function, max_queue_size=0, *args, **kwargs):
		log.debug(utils.method.msg_kw())
		cb = SmartCallable.bind_if_func(async_function, self, args=args, kwargs=kwargs)
		with self._lock:
			registered_task_count = self.registered_task_count(cb)
			return self._schedule_task(cb, registered_task_count, max_queue_size)
	
	# Schedule a function to run providing the max_queue_size that is less than the total amount of this function among the tasks in the queue
	@allow_any_thread
	def schedule_function(self, async_function, max_queue_size=0, *args, **kwargs):
		cb = SmartCallable.bind_if_func(async_function, self, args=args, kwargs=kwargs)
		with self._lock:
			registered_function_count = self.registered_task_count(cb)
			return self._schedule_task(cb, registered_function_count, max_queue_size)

	def run_parallel_task(self, async_function):
		raise "Not implemented yet."

	@allow_any_thread
	def run_until_complete(self, awaitable):
		log.debug(utils.method.msg_kw())
		try:
			log.debug(utils.method.msg_kw(f"Trying to check if the tasks are under processing by the owner thread"))
			with self._loop_operator.try_use(self.loop) as operator:
				try_result = operator.try_result()
				if try_result is True:
					log.debug(utils.method.msg_kw(f"Running the task until complete"))
					result = self.loop.run_until_complete(awaitable)
					log.verbose(utils.method.msg_kw(f"run_until_complete result: {result}"))
				else:
					if operator.is_operating_in_current_thread():
						raise RuntimeError(utils.method.msg_kw("Called run_until_complete() from a running task."))

					log.debug(utils.method.msg_kw(f"Called run_until_complete() from a different thread. Waiting the task to complete by the loop-owner thread '{operator.thread_id}'"))

					stop_waiting_event = threading.Event()

					def on_future_done(future):
						log.debug(utils.method.msg_kw(f"Task done: {future}"))
						stop_waiting_event.set()

					future = asyncio.run_coroutine_threadsafe(awaitable, self.loop)
					future.add_done_callback(on_future_done)

					def on_operator_released(operator_thread_id):
						log.debug(utils.function.msg_kw(f"Operator '{operator_thread_id}' released the loop"))
						stop_waiting_event.set()

					self._loop_operator.on_released.subscribe(on_operator_released)

					verify(stop_waiting_event.wait(4), utils.method.msg_kw("Waiting for the task to complete has timed out"))

					if not future.done():
						if not self._loop_operator.is_operating():
							log.debug(utils.method.msg_kw("Operator abandoned the task. Trying to perform it in the current thread"))
							with self._loop_operator(self.loop):
								task = asyncio_utils.task(awaitable, self.loop)
								if task is None:
									self.loop.run_until_complete(asyncio.sleep(0)) # Make sure the task has been created. It also can complete the task and the future.
									task = asyncio_utils.task(awaitable, self.loop)
								if task is None:
									verify(future.done(), utils.method.msg_kw("Task must have been created after performing a small update in the loop"))
									log.debug("Task has been completed during the small update in the loop")
								else:
									self.loop.run_until_complete(task)
						else:
							log.debug("Operator abandoned the task for a short period and is operating it again. Waiting for the task to complete")
					result = future.result()
					log.verbose(utils.method.msg_kw(f"Other thread run_until_complete result: '{result}'"))
		except Exception as e:
			log.error(utils.method.msg_kw(f"BaseException occurred while running the awaitable: '{e!r}'"))
			raise
		except asyncio.CancelledError as e:
			log.error(utils.method.msg_kw(f"CancelledError occurred while running the awaitable"))
			raise
		return result

	def _wait_futures(self, futures, timeout=None):
		log.debug(utils.method.msg_kw())
		async def wait_for_all_futures(futures, timeout=None):
			done, pending = await asyncio.wait_for(futures, timeout=timeout)
			for future in done:
				exception = future.exception()
				if exception is None:
					log.debug(utils.function.msg(f"Future completed with result: {future.result()}"))
				else:
					log.debug(utils.function.msg(f"Future raised an exception: {exception}"))
			log.debug(utils.function.msg(f"Done {len(done)} / {len(futures)} futures"))
			if pending:
				log.debug(utils.function.msg(f"Timeout occurred. {len(pending)} futures did not complete."))
				for future in pending:
					log.debug(utils.function.msg(f"Future did not complete yet: {future}"))
			return done, pending

		# Run the coroutine that waits for all futures in the provided event loop
		wait_future = asyncio.run_coroutine_threadsafe(wait_for_all_futures(futures, timeout), self.loop)
		
		# Block until the wait_future is done
		concurrent_done = concurrent.futures.wait([wait_future])[0]
		exc = wait_future.exception()
		if exc is None:
			if wait_future in concurrent_done:
				return wait_future.result()
			raise RuntimeError(utils.method.msg_kw("The wait_future is not done, but no exception occurred"))
		log.error(utils.method.msg_kw(f"An exception occurred: {exc}"))
		raise exc

	async def _run_until_complete_for_async(self, tasks_or_futures, timeout=None):
		log.debug(utils.method.msg(f"timeout={timeout}"))
		# Wait for the event in place of tasks to avoid the task cancellation
		event = asyncio.Event()
		name_type = "task" if isinstance(tasks_or_futures[0], asyncio.Task) else "future"
		remaining, count_to_wait = 0, 0
		def on_done(task_or_future):
			nonlocal remaining
			remaining -= 1
			log.debug(utils.function.msg(f"{name_type.capitalize()} done: '{task_or_future}'. Remaining: {remaining}"))
			if remaining == 0:
				event.set()
				log.debug(utils.function.msg(f"All {count_to_wait} {name_type}s are done"))
		for task_or_future in tasks_or_futures:
			if not task_or_future.done():
				task_or_future.add_done_callback(on_done)
				count_to_wait += 1
		remaining = count_to_wait
		if remaining == 0:
			log.debug(utils.function.msg(f"No {name_type}s to wait for"))
			return None
		log.debug(utils.function.msg(f"Waiting for {remaining} {name_type}s to complete"))
		result = await asyncio.wait_for(event.wait(), timeout=timeout)
		log.debug(utils.function.msg(f"Waiting for {name_type}s completed with result: {result}"))
		return result


	@allow_any_thread
	def wait_all_tasks(self, timeout=None):
		log.debug(utils.method.msg_kw())
		if self._loop_operator.is_operating_in_current_thread():
			raise RuntimeError(utils.method.msg_kw("Called wait_all_tasks() from a running task."))
		task_infos = self._tasks
		if len(task_infos) == 0:
			log.debug(utils.method.msg_kw("Nothing to wait for"))
			return self.WaitForResult()
		tasks = []
		futures = []
		for task_info in list(task_infos.values()):
			tasks.append(task_info.task)
			futures.append(task_info.future)
		return self.run_until_complete_for(tasks, timeout)
	

	@allow_any_thread
	# Returns the result of the future in the case of a successful completion
	def wait(self, future):
		verify(self._loop is not None and future.get_loop() == self._loop, utils.method.msg_kw("Foreign future provided"))
		try:
			return self.run_until_complete(future)
		except Exception as e:
			log.error(utils.function.msg_kw(f"Exception occurred while waiting for the future: '{e!r}'"))
		except asyncio.CancelledError as e:
			log.error(utils.function.msg_kw(f"CancelledError occurred while waiting for the future: '{e!r}'"))
		results, done, not_done = asyncio_utils.collect_results([future])
		return results[0]

	def run_until_complete_for(self, tasks_or_futures, timeout):
		log.debug(utils.method.msg_kw())
		name_type = "task" if isinstance(tasks_or_futures[0], asyncio.Task) else "future"
		def collect_results(timedout):
			results, done, not_done = asyncio_utils.collect_results(tasks_or_futures)
			return self.WaitForResult(done, not_done, results, timedout)
		try:
			self.run_until_complete(self._run_until_complete_for_async(tasks_or_futures, timeout))
			return collect_results(False)
		except asyncio.TimeoutError:
			log.debug(utils.method.msg_kw(f"Timeout occurred while completing the {name_type}s with timeout {timeout}"))
			return collect_results(True)
		except asyncio.CancelledError:
			log.debug(utils.method.msg_kw(f"CancelledError occurred while completing the {name_type}s with timeout {timeout}"))
			return collect_results(True)
		return collect_results(False)

	@allow_any_thread
	# Returns False in the case of a timeout. Otherwise, always True
	def complete_all_tasks(self, timeout=None):
		result = self.wait_all_tasks(timeout)
		if not result:
			log.debug(utils.method.msg_kw("Timeout occurred while completing all tasks. Cancelling all tasks"))
			self.cancel_all_tasks()
		return result


	class WaitForResult:
		def __init__(self, done=None, not_done=None, result=None, timedout=None):
			self.done = done
			self.not_done = not_done
			self.result = result
			self.timedout = timedout

		def __bool__(self):
			return not self.timedout

	@allow_any_thread
	# Returns WaitForResult object that contains the result of the future in the case of a successful completion and a timedout flag
	def wait_for(self, future, timeout):
		result = self.run_until_complete_for([future], timeout)
		if result.result is not None:
			result.result = result.result[0] if result.result else None
		return result

	def cancel_all_tasks(self):
		log.debug(utils.method.msg_kw(f"Cancelling {len(self._tasks)} tasks"))
		self._queue.clear()
		for task_info in list(self._tasks.values()):
			task_info.task.cancel()
		result = self.wait_all_tasks()
		verify(not result.not_done, utils.method.msg_kw("There are still not done tasks"))

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
			with self._loop_operator.try_use(self.loop) as operator:
				if operator.try_result() is True:
					self.loop.run_until_complete(update_task()) # Perform the pending or finalize the cancelled task
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

	@allow_any_thread_with_lock("_lock")
	def registered_task_count(self, function=None):
		return self.task_in_work_count(function) + self.queue_size(function)
	
	@allow_any_thread_with_lock("_lock")
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
		with self._lock:
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
			self.on_released = OneTimeSubscription()

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
					self.operator.on_released.reset_result()

			def _is_operating(self):
				is_operating = self.operator.is_operating()
				if not is_operating:
					if self.loop.is_running():
						raise RuntimeError("Unknown operator is already running the loop")
				return is_operating

			@safe_enter
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
					self.operator.on_released.set_result(operator_thread_id)
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

			@safe_enter
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
				self._try_result = not is_operating or self.operator.is_operating_in_current_thread()


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


def _check_future_task_cancelled(future, task):
	if future.cancelled():
		log.debug(utils.method.msg_kw(f"Future has been cancelled"))
		if not task.cancelled():
			# log.debug(utils.method.msg_kw(f"Cancelling the task"))
			task.cancel()
			log.debug(utils.method.msg_kw(f"  Cancelled the task"))
		else:
			log.debug(utils.method.msg_kw(f"  Task is already cancelled"))
	elif task.cancelled():
		log.debug(utils.method.msg_kw(f"Task has been cancelled"))
		if not future.done():
			# log.debug(utils.method.msg_kw(f"Cancelling the future"))
			future.cancel()
			log.debug(utils.method.msg_kw(f"  Cancelled the future"))
		else:
			log.debug(utils.method.msg_kw(f"  Future is already done"))
	else:
		return False
	return True
