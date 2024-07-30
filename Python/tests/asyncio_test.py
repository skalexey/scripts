import asyncio
import concurrent.futures
import time
from time import sleep

import utils.asyncio_utils as asyncio_utils
import utils.function
from utils.live import verify

from tests.test import *


async def sleep_task_job(sleep_time=0.3):
	try:
		log(utils.function.msg_kw(f"Started"))
		sleep_period = 0.01
		_slept = 0
		while _slept < sleep_time:
			_slept += sleep_period
			log(utils.function.msg(f"Effectively slept for {round(_slept, 2)} / {round(sleep_time, 2)} sec"))
			await asyncio.sleep(sleep_period)
		log(utils.function.msg("Woke Up!"))
	except BaseException as e:
		log(utils.function.msg(f"Exception caught: '{e}'"))
		raise
	return "Woke Up"

def simple_test():
	log(title("Simple Test"))
	async def task():
		log("Task started")
		await asyncio.sleep(1)
		log("Task completed")

	async def main():
		# Create a task but don't await it
		t = asyncio.create_task(task())

		# Check if the task is done
		if t.done():
			log("Task is done")
		else:
			log("Task is not done")

		# Function exits without awaiting the task
		log("Function exiting")

	# Run the event loop
	asyncio.run(main())

	log(title("End of Simple Test"))

def parallel_future_waiting_test():
	log(title("Parallel Future Waiting Test"))
	async def my_coroutine():
		log(f"Coroutine is running in thread {threading.current_thread().name}")
		await asyncio.sleep(1)
		return 'Coroutine Result'

	def start_event_loop(loop):
		log(utils.function.msg("Event loop started"))
		asyncio.set_event_loop(loop)
		loop.run_forever()
		log(utils.function.msg("Event loop stopped"))

	def wait_for_future(future, thread_name):
		log(f"Thread {thread_name} waiting for the future result")
		result = future.result()  # This will block until the future is done
		log(f"Thread {thread_name} got the result: {result}")
		log(f"Result once again: {future.result()}")

	# Create a new event loop
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	loop_thread.start()

	# Schedule the coroutine to run in the event loop and get a thread-safe future
	future = asyncio.run_coroutine_threadsafe(my_coroutine(), loop)

	# Create multiple threads that will wait for the same future
	threads = []
	for i in range(3):
		thread = threading.Thread(target=wait_for_future, args=(future, f"WorkerThread-{i+1}"))
		thread.start()
		threads.append(thread)

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()

	log(title("End of Parallel Future Waiting Test"))

def wait_for_a_future_with_timeout():
	async def my_coroutine():
		log(f"Coroutine is running in thread {threading.current_thread().name}")
		await asyncio.sleep(2)  # Simulate a long-running task
		return 'Coroutine Result'

	def start_event_loop(loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	def wait_for_future_with_timeout(future, thread_name, timeout):
		log(f"Thread {thread_name} waiting for the future result with timeout of {timeout} seconds")
		try:
			result = future.result(timeout=timeout)  # This will block until the future is done or timeout occurs
			log(f"Thread {thread_name} got the result: {result}")
		except concurrent.futures.TimeoutError:
			log(f"Thread {thread_name} timed out while waiting for the result")

	# Create a new event loop
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	loop_thread.start()

	# Schedule the coroutine to run in the event loop and get a thread-safe future
	future = asyncio.run_coroutine_threadsafe(my_coroutine(), loop)

	# Create multiple threads that will wait for the same future with a timeout
	threads = []
	for i in range(3):
		thread = threading.Thread(target=wait_for_future_with_timeout, args=(future, f"WorkerThread-{i+1}", 0.15))
		thread.start()
		threads.append(thread)

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()


def wait_for_several_futures_with_timeout(timeout=None):
	async def my_coroutine(task_id):
		log(f"Coroutine {task_id} is running in thread {threading.current_thread().name}")
		if task_id == 1:
			raise Exception(f"Coroutine {task_id} raised an exception")
		await asyncio.sleep((task_id + 1) * 0.1)  # Simulate a varying long-running task
		return f'Coroutine Result {task_id}'

	def start_event_loop(loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	def wait(futures, timeout):
		log(f"Waiting for all futures to complete with a timeout of {timeout} seconds")
		done, not_done = concurrent.futures.wait(futures, timeout=timeout, return_when=concurrent.futures.ALL_COMPLETED)
		log(f"Completed {len(done)} / {len(futures)} tasks")
		for future in done:
			try:
				result = future.result()  # This will get the result of the future
				log(f"Future completed with result: {result}")
			except Exception as e:
				log(f"Future raised an exception: {e}")

		for future in not_done:
			log(f"Future did not complete yet: {future}")
		
		if not_done:
			log(f"Timeout occurred. {len(not_done)} futures did not complete.")

	# Create a new event loop
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	loop_thread.start()

	# Schedule multiple coroutines to run in the event loop and get thread-safe futures
	futures = [asyncio.run_coroutine_threadsafe(my_coroutine(i), loop) for i in range(3)]

	# Wait for all futures to complete with a single timeout
	wait_thread = threading.Thread(target=wait, args=(futures, timeout))
	wait_thread.start()
	wait_thread.join()

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()

def wait_for_several_futures_with_timeout_noexcept(timeout=None):
	async def my_coroutine(task_id):
		log(f"Coroutine {task_id} is running in thread {threading.current_thread().name}")
		if task_id == 1:
			raise Exception(f"Coroutine {task_id} raised an exception")
		await asyncio.sleep((task_id + 1) * 0.1)  # Simulate a varying long-running task
		return f'Coroutine Result {task_id}'

	def start_event_loop(loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	def wait(futures, timeout):
		log(f"Waiting for all futures to complete with a timeout of {timeout} seconds")
		done, not_done = concurrent.futures.wait(futures, timeout=timeout, return_when=concurrent.futures.ALL_COMPLETED)
		log(f"Completed {len(done)} / {len(futures)} tasks")

		for future in done:
			if future.exception() is None:
				result = future.result()  # This will get the result of the future
				log(f"Future completed with result: {result}")
			else:
				exception = future.exception()
				log(f"Future raised an exception: {exception}")

		for future in not_done:
			log(f"Future did not complete yet: {future}")

		if not_done:
			log(f"Timeout occurred. {len(not_done)} futures did not complete.")

	# Create a new event loop
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	loop_thread.start()

	# Schedule multiple coroutines to run in the event loop and get thread-safe futures
	futures = [asyncio.run_coroutine_threadsafe(my_coroutine(i), loop) for i in range(3)]

	# Wait for all futures to complete with a single timeout
	wait_thread = threading.Thread(target=wait, args=(futures, timeout))
	wait_thread.start()
	wait_thread.join()

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()

def wait_asyncio_futures_with_timeout(timeout=None):
	def start_event_loop(loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	def wait(futures, loop, timeout=None):
		async def wait_for_all_futures(futures, timeout):
			log(f"Waiting for {len(futures)} futures to complete with a timeout of {timeout} seconds")
			done, pending = await asyncio.wait(futures, timeout=timeout)
			
			results = []
			for future in done:
				if future.exception() is None:
					results.append(future.result())  # Get the result of the future
					log(f"Future completed with result: {future.result()}")
				else:
					exception = future.exception()
					log(f"Future raised an exception: {exception}")
			
			for future in pending:
				log(f"Future did not complete yet: {future}")
			
			if pending:
				log(f"Timeout occurred. {len(pending)} futures did not complete.")
			
			return results, pending

		# Run the coroutine that waits for all futures in the provided event loop
		wait_future = asyncio.run_coroutine_threadsafe(wait_for_all_futures(futures, timeout), loop)
		
		try:
			results, pending = wait_future.result()  # Wait for the completion
			return results, pending
		except concurrent.futures.TimeoutError:
			log("Timeout while waiting for the futures")
			return [], futures
		except Exception as e:
			log(f"An exception occurred: {e}")
			return [], futures
		
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	loop_thread.start()

	# Create multiple futures
	futures = [loop.create_future() for _ in range(3)]

	# Simulate setting results for the futures after some delay
	async def set_futures():
		await asyncio.sleep(0.1)
		futures[0].set_result('Result 1')
		await asyncio.sleep(0.1)
		futures[1].set_result('Result 2')
		await asyncio.sleep(0.1)
		futures[2].set_result('Result 3')

	asyncio.run_coroutine_threadsafe(set_futures(), loop)

	# Wait for the futures to complete with a single timeout
	results, pending = wait(futures, loop, timeout=0.5)

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()

	log(f"Results: {results}")
	log(f"Pending futures: {pending}")
	

def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def wait_for_asyncio_futures_with_timeout_multithread(timeout=None):
	def wait(futures, loop, timeout=None):
		async def wait_for_all_futures(futures, timeout):
			log(utils.function.msg(f"Waiting for {len(futures)} futures to complete with a timeout of {timeout} seconds"))
			done, pending = await asyncio.wait(futures, timeout=timeout)
			for future in done:
				exception = future.exception()
				if future.exception() is None:
					log(utils.function.msg(f"Future {future} completed with result: {future.result()}"))
				else:
					log(utils.function.msg(f"Future {future} raised an exception: {exception}"))
			log(utils.function.msg(f"Done {len(done)} / {len(futures)} tasks"))
			if pending:
				log(utils.function.msg(f"Timeout occurred. {len(pending)} futures did not complete."))
				for future in pending:
					log(utils.function.msg(f"Future did not complete yet: {future}"))
			return done, pending

		# Run the coroutine that waits for all futures in the provided event loop
		wait_future = asyncio.run_coroutine_threadsafe(wait_for_all_futures(futures, timeout), loop)
		
		# Block until the wait_future is done
		done, not_done = concurrent.futures.wait([wait_future])
		assert wait_future in done
		if wait_future in done:
			exc = wait_future.exception()
			if exc is None:
				results, pending = wait_future.result()  # Get the result if no exception occurred
				return results, pending
			else:
				log(utils.function.msg_kw(f"An exception occurred: {exc}"))
				return [], futures
		else:
			log(utils.function.msg_kw("Timeout while waiting for the futures"))
			return [], futures

	def thread_wait_for_futures(name, futures, loop, timeout):
		log(utils.function.msg_kw(f"Thread {name} is waiting for futures"))
		results, pending = wait(futures, loop, timeout)
		log(utils.function.msg(f"Thread {name} finished waiting with results: {results} and pending: {pending}"))

	# Create a new event loop
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	loop_thread.start()

	# Create multiple futures
	futures = [loop.create_future() for _ in range(3)]

	# Simulate setting results for the futures after some delay
	async def set_futures():
		await asyncio.sleep(0.1)
		futures[0].set_result('Result 1')
		await asyncio.sleep(0.1)
		futures[1].set_exception(RuntimeError('Future 2 raised an exception'))
		await asyncio.sleep(0.1)
		futures[2].set_result('Result 3')

	asyncio.run_coroutine_threadsafe(set_futures(), loop)

	# Create multiple threads that wait for the same pack of futures
	threads = []
	for i in range(3):
		thread = threading.Thread(target=thread_wait_for_futures, args=(f"WorkerThread-{i+1}", futures, loop, timeout))
		thread.start()
		threads.append(thread)

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()

def wait_and_complete_tasks_test_2(timeout):
	def start_event_loop(loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	async def example_task(task_id):
		await asyncio.sleep(0.1 * task_id)
		return f'Result {task_id}'

	def run_tasks_with_timeout(tasks, timeout):
		async def run_all_tasks():
			# Schedule the tasks and gather their results
			return await asyncio.gather(*tasks, return_exceptions=True)

		# Run the tasks in the event loop with a timeout
		future = asyncio.run_coroutine_threadsafe(run_all_tasks(), loop)

		done, not_done = concurrent.futures.wait([future], timeout=timeout)

		if future in done:
			# The future is done, check for exceptions
			exc = future.exception()
			if exc is None:
				results = future.result()
				log(f"All tasks completed with results: {results}")
			else:
				log(f"An exception occurred: {exc}")
		else:
			log("Timeout reached")

	def launch_tasks_from_thread(tasks, timeout):
		thread = threading.Thread(target=run_tasks_with_timeout, args=(tasks, timeout))
		thread.start()
		thread.join()

	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	# Create and schedule multiple tasks
	tasks = [loop.create_task(example_task(i)) for i in range(1, 4)]

	# Launch tasks from a thread with a timeout
	launch_tasks_from_thread(tasks, timeout)

def wait_and_complete_tasks_test_3(timeout):
	async def example_task(task_id):
		await asyncio.sleep(0.1 * task_id)
		return f'Result {task_id}'

	def run_tasks_with_timeout(loop, tasks, timeout):
		async def run_all_tasks():
			# Schedule the tasks and gather their results
			return await asyncio.gather(*tasks, return_exceptions=True)

		# Submit the coroutine to run the tasks in the event loop
		future = asyncio.run_coroutine_threadsafe(run_all_tasks(), loop)

		# Wait for the future to complete with a timeout
		done, not_done = concurrent.futures.wait([future], timeout=timeout)

		if future in done:
			# The future is done, check for exceptions
			exc = future.exception()
			if exc is None:
				results = future.result()
				log(f"All tasks completed with results: {results}")
			else:
				log(f"An exception occurred: {exc}")
		else:
			log("Timeout reached. Cancelling pending tasks...")
			# Cancel all pending tasks
			for task in tasks:
				task.cancel()
			try:
				results = future.result()  # Get the results of the cancelled tasks
				log(f"Results after cancellation: {results}")
			except Exception as e:
				log(f"Exception after cancellation: {e}")

	def launch_tasks_from_thread(loop, tasks, timeout):
		asyncio.set_event_loop(loop)
		run_tasks_with_timeout(loop, tasks, timeout)

	# Create a single event loop
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	# Create and schedule multiple tasks
	tasks = [example_task(i) for i in range(1, 4)]
	tasks = [loop.create_task(task) for task in tasks]

	# Launch tasks from multiple threads with a timeout
	threads = []
	for i in range(3):
		thread = threading.Thread(target=launch_tasks_from_thread, args=(loop, tasks, 0.5))
		thread.start()
		threads.append(thread)

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

#######
def wait_and_complete_tasks_test(timeout):
	def start_event_loop(loop):
		asyncio.set_event_loop(loop)
		loop.run_forever()

	async def example_task(task_id):
		log(utils.function.msg(f"Task {task_id} is running in thread {threading.current_thread().name}"))
		await asyncio.sleep(0.1 * task_id)
		log(utils.function.msg(f"Task {task_id} completed"))
		return f'Result {task_id}'

	def wait_for_task_completion(task, loop, results, cancel_event):
		if cancel_event.is_set():
			log(f"Task was cancelled before starting")
			return None
		try:
			# If the task is already done, get the result directly
			if task.done():
				result = task.result()
			else:
				async def run_task():
					return await task
				# Wait for the task to complete
				future = asyncio.run_coroutine_threadsafe(run_task(), loop)
				result = future.result()
			log(f"Task completed with result: {result}")
			results.append(result)
			return result
		except asyncio.CancelledError:
			log("Task was cancelled during execution")
			raise
		except Exception as e:
			log(f"Task raised an exception: {e}")
			raise

	def complete_tasks(tasks, loop, timeout=None):
		completed, not_completed = [], []
		try:
			# If the task is already done, get the result directly
			not_completed_tasks = []
			for task in tasks:
				if task.done():
					completed.append(task)
				else:
					not_completed.append(task)
			if completed:
				log(f"Already completed tasks: {completed}")
			if not_completed:
				log(f"Completing {len(not_completed)} remaining tasks")
				async def run_tasks():
					log("Running tasks")
					await asyncio.sleep(0.1)
					#return await asyncio.gather(*not_completed)
				# Wait for the tasks to complete
				loop.run_until_complete(run_tasks())
				future = asyncio.run_coroutine_threadsafe(run_tasks(), loop)
				result = future.result()
				log(f"Tasks completed with results: {result}")
				concurrent_done = [future]
				# concurrent_done = concurrent.futures.wait([future], timeout=timeout, return_when=concurrent.futures.ALL_COMPLETED)[0]
				exc = future.exception()
				if exc is not None:
					log(f"An exception occurred: {exc}")
					raise exc
				if concurrent_done:
					completed.extend(not_completed)
				else:
					not_completed_updated = []
					for task in not_completed:
						if task.done():
							completed.append(task)
						else:
							not_completed_updated.append(task)
					not_completed = not_completed_updated
			return completed, not_completed
		except asyncio.CancelledError:
			log(utils.function.msg("Gather task was cancelled during execution"))
			raise
		except Exception as e:
			log(utils.function.msg(f"Task raised an exception: {e}"))
			raise


	def thread_wait_and_complete_tasks(name, tasks, loop, timeout):
		log(f"Thread {name} is waiting for tasks with timeout of {timeout} seconds")
		try:
			def job():
				done, not_done = complete_tasks(tasks, loop, timeout)
				if not_done:
					log(utils.function.msg(f"Timeout occurred while waiting for tasks"))
				else:
					results = [f"{task}, result: {task.result()}" for task in done]
					log(utils.function.msg(f"Completed tasks with results: {results}"))
			thread = threading.Thread(target=job, name=name)
			thread.start()
			thread.join()
		except Exception as e:
			log(f"An exception in a thread occurred: {e}")

	# Create a new event loop
	loop = asyncio.new_event_loop()

	# Start the event loop in a new thread
	# loop_thread = threading.Thread(target=start_event_loop, args=(loop,), name='LoopThread')
	# loop_thread.start()

	# Create and schedule multiple tasks
	tasks = [loop.create_task(example_task(i)) for i in range(1, 4)]

	# Create multiple threads that wait for the same pack of tasks
	threads = []
	for i in range(3):
		thread = threading.Thread(target=thread_wait_and_complete_tasks, args=(f"WorkerThread-{i+1}", tasks, loop, timeout))
		thread.start()
		threads.append(thread)

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	# Stop the event loop
	loop.call_soon_threadsafe(loop.stop)
	loop_thread.join()


def wait_tasks_through_event(timeout=None):
	async def wait_for_tasks_completion(task_infos, loop, timeout):
		event = asyncio.Event()
		remaining, task_count_to_wait = 0, 0
		def on_task_done(task_info):
			nonlocal remaining
			remaining -= 1
			log.debug(utils.function.msg(f"Task done: {task_info}. Remaining: {remaining}"))
			if remaining == 0:
				event.set()
				log.debug(utils.function.msg(f"All {task_count_to_wait} tasks are done"))
		for task_info in task_infos:
			if not task_info.task.done():
				task_info.on_done.subscribe(on_task_done)
				task_count_to_wait += 1
		remaining = task_count_to_wait
		log.debug(utils.function.msg(f"Waiting for {remaining} tasks to complete"))
		result = await asyncio.wait_for(event.wait(), timeout=timeout)
		log.debug(utils.function.msg(f"Waiting for tasks completed with result: {result}"))
		return result


	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	# Create and schedule multiple tasks
	task_infos = []

	class TaskInfo:
		def __init__(self, task):
			self.task = task
			self.on_done = Subscription()

	for i in range(1, 4):
		log.debug(utils.function.msg(f"Creating task {i}"))
		task = loop.create_task(sleep_task_job())
		task_info = TaskInfo(task)
		def on_done(task):
			log.debug(utils.function.msg(f"Task {task_info} is done"))
			task_info.on_done.notify(task_info)
		task.add_done_callback(on_done)
		task_infos.append(task_info)

	result = loop.run_until_complete(wait_for_tasks_completion(task_infos, loop, timeout))
	return result

def periodic_loop_check_test():
	loop = asyncio.new_event_loop()
	# Create a new coroutine each time by defining a function that returns a new coroutine instance
	def create_example_coroutine(loop):
		# async def example_coroutine():
		# 	log(utils.function.msg("Coroutine started"))
		# 	await asyncio.sleep(1)  # Increase sleep time to simulate long-running task
		# 	log(utils.function.msg("Coroutine completed"))
		# 	return "Task Completed"
		# return example_coroutine()
		# return asyncio.ensure_future(sleep_task_job(1))
		return sleep_task_job(1)

	def start_event_loop(loop):
		log(utils.function.msg("Loop thread started"))
		asyncio.set_event_loop(loop)
		loop.run_forever()
		log(utils.function.msg("Loop thread finished"))

	def stop_event_loop(loop, delay):
		log(utils.function.msg("Stop thread started"))
		time.sleep(delay)
		loop.stop()
		log(utils.function.msg("Stop thread stopped"))

	def monitor_loop(loop, coro, loop_future):
		log(utils.function.msg("Monitor started"))
		while loop.is_running():
			time.sleep(0.1)  # Check every 100ms
		log(utils.function.msg("Loop stopped. Continuing with the task in the Monitor Thread"))
		if not loop_future.done():
			log(utils.function.msg("Running task directly in monitor thread"))
			# result = loop.run_until_complete(coro)
			# task = asyncio.ensure_future(coro, loop=loop)
			task = asyncio_utils.task(coro, loop)
			result = loop.run_until_complete(task)
			# Running it again must effectively do nothing as it was completed
			result = loop.run_until_complete(task)
			log(utils.function.msg("Running the task completed in monitor thread"))
		log(utils.function.msg("Monitor finished"))

	def run_task_directly_if_no_loop_running(coro):
		loop_future = concurrent.futures.Future()

		loop_thread = threading.Thread(target=start_event_loop, name="Loop", args=(loop,))
		loop_thread.start()

		# Give the loop a moment to start
		time.sleep(0.1)

		if loop.is_running():
			monitor_thread = threading.Thread(target=monitor_loop, name="Monitor", args=(loop, coro, loop_future))
			monitor_thread.start()
			try:
				task_future = asyncio.run_coroutine_threadsafe(coro, loop)
				def on_task_done(f):
					if f.done():
						loop_future.set_result(f.result())
				task_future.add_done_callback(on_task_done)
			except RuntimeError:
				loop.stop()
				result = loop.run_until_complete(coro)
				loop_future.set_result(result)
		else:
			result = loop.run_until_complete(coro)
			loop_future.set_result(result)

		# Stop the loop after a short delay to simulate the early stop
		stop_thread = threading.Thread(target=stop_event_loop, name="Stop", args=(loop, 0.5))
		stop_thread.start()

		# Wait for the loop thread to finish
		loop_thread.join()
		monitor_thread.join()
		stop_thread.join()

		return loop_future

	# Example usage
	future = run_task_directly_if_no_loop_running(create_example_coroutine(loop))
	print(future.result())  # Output: Task Completed


def coro_suspend_resume_test():
	class CoroutineController:
		def __init__(self):
			self._futures = {}

		async def perform_task(self):
			print("Task started, performing for 140ms...")
			self._futures['suspend'] = asyncio.Future()
			try:
				await asyncio.wait_for(self._futures['suspend'], timeout=0.14)
			except asyncio.TimeoutError:
				print("Task suspended at 140ms, waiting to resume...")

			# Wait until resumed
			self._futures['resume'] = asyncio.Future()
			await self._futures['resume']

			print("Task resumed, continuing execution...")
			# Simulate finishing the task
			await asyncio.sleep(0.3)
			print("Task completed.")

		async def run_with_suspend(self):
			task = asyncio.create_task(self.perform_task())

			# Let the task run for at least 200ms
			await asyncio.sleep(0.2)
			if not self._futures['suspend'].done():
				self._futures['suspend'].set_result(True)

			return task

		def resume_task(self):
			if 'resume' in self._futures:
				self._futures['resume'].set_result(True)

	async def main():
		controller = CoroutineController()

		# Run the task and suspend it after 200ms
		task = await controller.run_with_suspend()

		# Simulate doing something else
		print("Main coroutine doing other work...")

		await asyncio.sleep(1)

		# Resume the task
		print("Resuming task...")
		controller.resume_task()

		# Wait for the task to complete
		await task

	asyncio.run(main())


def submit_task_threadsafe_test():
	loop = asyncio.new_event_loop()
	async def coro():
		log("Coroutine started")
		await asyncio.sleep(0.1)
		log("Coroutine completed")
		# Just for small test
	asyncio.run_coroutine_threadsafe(coro, loop)
	tasks = asyncio.all_tasks(loop)
	assert len(tasks) == 0
	loop.run_until_complete(asyncio.sleep(0))
	assert len(asyncio.all_tasks(loop)) == 1
	task = asyncio_utils.task(coro, loop)
	assert task._coro == coro
	
def coro_comparison_test():
	log(title("Coroutine Comparison Test"))
	async def coro():
		await asyncio.sleep(0.1)
		return "Coroutine Result"
	
	coro1 = coro()
	coro2 = coro()
	assert coro1 != coro2

	log(title("End of Coroutine Comparison Test"))

def concurrent_future_test():
	log(title("Concurrent Future Test"))
	future = concurrent.futures.Future()
	assert future.done() == False
	future.set_result("Result")
	assert future.done() == True
	
	def on_done(f):
		assert f.done() == True
		assert f.result() == "Result"
		log("Future done")

	future.add_done_callback(on_done)
	assert future.done() == True
	log(title("End of Concurrent Future Test"))
	
def test():
	# simple_test()
	# parallel_future_waiting_test()
	# wait_for_a_future_with_timeout()
	# wait_for_several_futures_with_timeout()
	# wait_for_several_futures_with_timeout(0.21)
	# wait_for_several_futures_with_timeout(3)
	# wait_for_several_futures_with_timeout_noexcept(0.21)
	# wait_for_several_futures_with_timeout_noexcept(3)
	# wait_asyncio_futures_with_timeout(0.21)
	# wait_for_asyncio_futures_with_timeout_multithread(0.21)
	# wait_for_asyncio_futures_with_timeout_multithread(1.31)
	# wait_and_complete_tasks_test(0.1)
	# wait_and_complete_tasks_test(0.2)
	# wait_and_complete_tasks_test_2(0.9)
	# wait_and_complete_tasks_test_3(0.9)
	# wait_tasks_through_event()
	periodic_loop_check_test()
	# coro_suspend_resume_test()
	# submit_task_threadsafe_test()
	# coro_comparison_test()
	# concurrent_future_test()

run()
