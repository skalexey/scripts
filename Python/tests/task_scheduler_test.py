import asyncio
import threading
from test import *
from time import sleep, time

import utils.method
import utils.profile.profiler
import utils.text
from utils.profile.trackable_resource import TrackableResource
from utils.task_scheduler import TaskScheduler


class A(TaskScheduler):
	async def async_method1(self):
		log("Task 1 started")
		await asyncio.sleep(1)
		log("Task 1 completed")
		return "Success 1"

	async def async_method2(self):
		log("Task 2 started")
		await asyncio.sleep(1)
		log("Task 2 completed")
		return "Success 2"

	async def async_method3(self):
		log("Task 3 started")
		await asyncio.sleep(1)
		log("Task 3 completed")
		return "Success 3"

	def parallel_test(self):
		log(title("Parallel test", "=", 60))
		result_future = self.run_parallel_task(self.async_method1)
		result_future = self.run_parallel_task(self.async_method2)
		result_future = self.run_parallel_task(self.async_method3)
		self.validate_task_count(3, 3, 0)
		profiler.start()
		self.wait_all_tasks()
		profiler.print_measure()
		log(title("Parallel test completed"))

	def queue_test(self):
		log(title("Queue test"))
		result_future = self.schedule_task(self.async_method1, 6)
		result_future = self.schedule_task(self.async_method1, 6)
		result_future = self.schedule_task(self.async_method1, 6)
		result_future = self.schedule_task(self.async_method2, 6)
		result_future = self.schedule_task(self.async_method2, 6)
		result_future = self.schedule_task(self.async_method2, 6)
		self.validate_task_count(6, 5, 1)
		profiler.start()
		self.wait_all_tasks()
		profiler.print_measure()
		log(title("Queue test completed"))

	def validate_task_count(self, registered, enqueued, in_work):
		registered_task_count = self.registered_task_count()
		enqueued_task_count = self.queue_size()
		tasks_in_work_count = self.task_in_work_count()
		log(f"Tasks registered: {registered_task_count}, enqueued: {enqueued_task_count}, in work: {tasks_in_work_count}")
		assert registered_task_count == registered
		assert enqueued_task_count == enqueued
		assert tasks_in_work_count == in_work
		 
	def function_test(self):
		log("=== Function test ===")
		result_future = self.schedule_function(self.async_method1, 1)
		result_future = self.schedule_function(self.async_method1, 1)
		result_future = self.schedule_function(self.async_method1, 1)
		result_future = self.schedule_function(self.async_method2, 1)
		result_future = self.schedule_function(self.async_method2, 1)
		result_future = self.schedule_function(self.async_method2, 1)
		result_future = self.schedule_function(self.async_method3, 1)
		result_future = self.schedule_function(self.async_method3, 1)
		result_future = self.schedule_function(self.async_method3, 1)
		self.validate_task_count(6, 5, 1)
		profiler.start()
		self.wait_all_tasks()
		profiler.print_measure()
		log(title("Function test completed"))

	def test(self):
		log(title("Start the tests"))
		self.queue_test()
		self.function_test()
		log(title("Tests completed"))

def test1():
	log(title("Test 1"))
	a = A()
	log(title("End of Test 1"))

def report_resources_status():
	log(title("Resources status report"))
	resources = TrackableResource.resources
	log(f"Resources count: {len(resources)}")
	for i, resource in enumerate(resources):
		log(f"  Resource {i}: {resource}")
	log(title("End of Resources status report"))
	
def validation_test():
	assert issubclass(asyncio.TimeoutError, Exception)
	assert not issubclass(asyncio.CancelledError, Exception)
	assert issubclass(asyncio.CancelledError, BaseException)

def tasks_test():
	class A:
		def __init__(self):
			self.scheduler = TaskScheduler()
		
		def update(self, dt):
			self.scheduler.update(dt)

		async def async_method_sleep(self, sleep_time=0.3):
			try:
				log(utils.method.msg_kw(f"Started"))
				sleep_period = 0.01
				_slept = 0
				_start_time = time()
				while _slept < sleep_time:
					await asyncio.sleep(sleep_period)
					_slept = time() - _start_time
					log(utils.method.msg_kw(f"Effectively slept for {round(_slept, 2)} / {round(sleep_time, 2)} sec"))
				log(utils.method.msg_kw("Woke Up!"))
			except BaseException as e:
				log(utils.method.msg_kw(f"Exception caught: '{e!r}'"))
				raise
			return "Woke Up"

		async def async_method_wait(self):
			log(utils.method.msg_kw("Started"))
			self.scheduler.wait_all_tasks()
			log(utils.method.msg_kw("Completed"))

	a = A()

	def cancel_tasks_job():
		sleep(0.1) # Let the main thread to start performing the task for the second test
		a.scheduler.cancel_all_tasks()
		log("All tasks cancelled. Waiting for the tasks to complete by another thread")
		while a.scheduler.registered_task_count() > 0:
			sleep(0.01)

	def run_tasks_job():
		while a.scheduler.registered_task_count() > 0:
			a.update(1)
			log("Update done")

	def wait_all_tasks_test(single_thread=None, owner_timeout=None, waiter_timeout=None, sleep_time=None):
		log(title("Wait all tasks test"))
		_sleep_time = (owner_timeout * 2 if owner_timeout else 0.3) if sleep_time is None else sleep_time
		slept_time = 0
		owner_early_exit = _sleep_time > owner_timeout if owner_timeout is not None else False
		waiter_early_exit = True if single_thread else (_sleep_time > waiter_timeout if waiter_timeout is not None else False)
		wait_owner_str = 'for ' + str(owner_timeout) + ' seconds' if owner_timeout is not None else ' without timeout'
		wait_waiter_str = "" if single_thread else (' and ' + str(waiter_timeout) + ' seconds' if waiter_timeout is not None else ' and with no waiter timeout')
		log(f"Wait all tasks in {'a single thread' if single_thread else 'multiple threads'} {wait_owner_str}{wait_waiter_str} while sleeping for {_sleep_time} seconds ({'more' if owner_early_exit else 'less'} than the owner timeout)")
		a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=_sleep_time)
		assert a.scheduler.registered_task_count() == 1
		assert not a.scheduler.loop.is_running()

		lock = threading.Lock()

		def check_loop_job(timeout=None, expected_result=None):
			# assert not a.scheduler.loop.is_running()
			# while not a.scheduler.loop.is_running():
			# 	sleep(0.01)
			nonlocal slept_time, _sleep_time
			log("Waiting" + (f" with timeout {timeout}" if timeout else " until full completion"))
			local_profiler = utils.profile.profiler.TimeProfiler()
			local_profiler.start()
			result = a.scheduler.wait_all_tasks(timeout) # Wait for the tasks to complete from another thread: Ok
			measured_time = local_profiler.measure()
			log(f"Wait completed after {measured_time} seconds")
			expected_wait_time = timeout if timeout else (_sleep_time - slept_time)
			assert measured_time < expected_wait_time + 0.1
			assert measured_time > expected_wait_time - 0.1
			with lock:
				slept_time += measured_time
			if expected_result is not None:
				assert result.timedout == (not expected_result)

		if single_thread:
			check_loop_job(owner_timeout, expected_result=(not owner_early_exit))
		else:
			thread = threading.Thread(target=check_loop_job, name="Performer", args=(owner_timeout if owner_timeout is not None else None, owner_timeout is None)) # Performer, so without timeout
			thread.start()
			sleep(0.1)
			if waiter_timeout is not None:
				check_loop_job(waiter_timeout, expected_result=_sleep_time-0.1-waiter_timeout<=0)
				check_loop_job(waiter_timeout / 4, expected_result=_sleep_time-0.1-waiter_timeout*1.25<=0)
				check_loop_job(waiter_timeout, expected_result=_sleep_time-0.1-waiter_timeout*2.25<=0)
			else:
				check_loop_job(expected_result=True)
			log("Joining the performer thread")
			thread.join()
			log("Performer thread joined")
		assert a.scheduler.registered_task_count() == (1 if owner_early_exit and waiter_early_exit else 0)
		a.scheduler.cancel_all_tasks()
		log(title("End of Wait all tasks test"))

	def cancel_the_wait_task():
		log(title("Cancel the wait task"))
		f = a.scheduler.schedule_task(a.async_method_wait, 1)
		assert a.scheduler.registered_task_count() == 1
		f.cancel()
		a.update(1)
		assert a.scheduler.registered_task_count() == 0

	def cancel_the_wait_task_from_another_thread():
		log(title("Cancel the wait task from another thread"))
		f = a.scheduler.schedule_task(a.async_method_wait, 1)
		assert a.scheduler.registered_task_count() == 1

		thread = threading.Thread(target=cancel_tasks_job)
		thread.start()
		for i in range(3):
			sleep(0.2)
		assert a.scheduler.registered_task_count() == 0
		thread.join()

	def complete_tasks_in_parallel():
		log(title("Complete tasks in parallel"))
		f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=0.6)
		assert a.scheduler.registered_task_count() == 1

		thread = threading.Thread(target=run_tasks_job)
		thread.start()
		sleep(0.1)
		run_tasks_job()
		thread.join()

	def cancel_from_another_thread():
		log(title("Cancel from another thread"))
		f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=3)
		thread = threading.Thread(target=cancel_tasks_job)
		thread.start()
		run_tasks_job()
		thread.join()

	def wait_future():
		log(title("Wait future"))
		f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=0.6)
		assert a.scheduler.registered_task_count() == 1
		result = a.scheduler.wait(f)
		assert result == "Woke Up"

	def wait_all_and_cancel_from_another_thread():
		log(title("Wait all and cancel from another thread"))
		f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=3)
		thread = threading.Thread(target=cancel_tasks_job)
		thread.start()
		result = a.scheduler.wait_all_tasks()
		assert isinstance(result.result[0], asyncio.CancelledError)
		assert a.scheduler.registered_task_count() == 0
		log("Joining the canceller thread")
		thread.join(4)
		if thread.is_alive():
			raise Exception("Thread did not join in time")
		a.update(1)

	def wait_and_cancel_from_another_thread():
		log(title("Wait and cancel from another thread"))
		f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=3)
		thread = threading.Thread(target=cancel_tasks_job)
		thread.start()
		log(utils.function.msg_kw("Waiting for the task to complete"))
		result = a.scheduler.wait(f)
		assert isinstance(result, asyncio.CancelledError)
		assert a.scheduler.registered_task_count() == 0
		log(utils.function.msg_kw("Joining the canceller thread"))
		thread.join()
		a.update(1)

	def wait_with_timeout():
		def job(time_to_wait, time_to_sleep):
			f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=time_to_sleep)
			assert a.scheduler.registered_task_count() == 1
			log(f"Start waiting for {time_to_sleep} seconds")
			profiler.start()
			result = a.scheduler.wait_for(f, time_to_wait)
			assert result.result == (None if time_to_wait < time_to_sleep else "Woke Up")
			assert result.timedout == (True if time_to_wait < time_to_sleep else False)
			measured_time = profiler.measure()
			log(f"Wait completed after {measured_time} seconds")
			assert measured_time < time_to_wait + 0.05
			assert a.scheduler.registered_task_count() == (1 if time_to_wait < time_to_sleep else 0)
			a.scheduler.cancel_all_tasks()
			assert a.scheduler.registered_task_count() == 0
			return result
		
		log(title("Wait with timeout early exit"))
		result = job(0.13, 0.2)
		assert result.result == None

		log(title("Wait with too big timeout"))
		result = job(0.4, 0.2)
		assert result.result == "Woke Up"
		assert result.timedout == False

	def exception_test(timeout=None):
		log(title("Exception Test"))
		async def coro_with_exception():
			log("Task started")
			await asyncio.sleep(0.1)
			raise Exception("Task failed")
			log("Task completed")

		f = a.scheduler.schedule_task(coro_with_exception, 1)
		if timeout is None:
			result = a.scheduler.wait(f)
		else:
			result = a.scheduler.wait_for(f, timeout).result
		assert isinstance(result, Exception)
		log(f"Result: {result}")
		log(title("End of Exception Test"))

	report_resources_status()
	validation_test()
	wait_all_tasks_test(True)
	wait_all_tasks_test(False, 0.1)
	wait_all_tasks_test(True, 0.4)
	wait_all_tasks_test(False, 0.1)
	wait_all_tasks_test(False, 0.4, 0.26)
	cancel_the_wait_task()
	cancel_the_wait_task_from_another_thread()
	complete_tasks_in_parallel()
	wait_all_and_cancel_from_another_thread()
	wait_and_cancel_from_another_thread()
	wait_future()
	wait_with_timeout()
	exception_test()
	exception_test(110.2)

	

def test():
	log(title("Task Scheduler test"))
	validation_test()
	for i in range(99):
		log(utils.function.msg(f"Iteration {i}"))
		tasks_test()
	log(title("Task Scheduler test completed"))

run()