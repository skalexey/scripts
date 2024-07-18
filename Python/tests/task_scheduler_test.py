import asyncio
import threading
from test import *
from time import sleep

import utils.method
import utils.profile.profiler
import utils.text
from utils.log.logger import Logger
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

def wait_tasks_test():
	class A:
		def __init__(self):
			self.scheduler = TaskScheduler()
		
		def update(self, dt):
			self.scheduler.update(dt)

		async def async_method_sleep(self, sleep_time=0.3):
			log(utils.method.msg_kw(f"Started"))
			await asyncio.sleep(sleep_time)
			log(utils.method.msg_kw("Completed"))

		async def async_method_wait(self):
			log(utils.method.msg_kw("Started"))
			self.scheduler.wait_all_tasks()
			log(utils.method.msg_kw("Completed"))

	a = A()

	def cancel_tasks_job():
		sleep(0.1) # Let the main thread to start performing the task for the second test
		a.scheduler.cancel_all_tasks()
		while a.scheduler.registered_task_count() > 0:
			sleep(0.01)

	def run_tasks_job():
		while a.scheduler.registered_task_count() > 0:
			a.update(1)
			log("Update done")

	a.scheduler.schedule_task(a.async_method_sleep, 1)
	assert a.scheduler.registered_task_count() == 1
	assert not a.scheduler.loop.is_running()

	def check_loop_job():
		assert not a.scheduler.loop.is_running()
		while not a.scheduler.loop.is_running():
			sleep(0.01)
		a.scheduler.wait_all_tasks() # Wait for the tasks to complete from another thread: Ok

	thread = threading.Thread(target=check_loop_job)
	thread.start()
	sleep(0.1)
	a.scheduler.wait_all_tasks()
	thread.join()
	assert a.scheduler.registered_task_count() == 0

	log(title("Cancel the wait task"))
	f = a.scheduler.schedule_task(a.async_method_wait, 1)
	assert a.scheduler.registered_task_count() == 1
	f.cancel()
	a.update(1)
	assert a.scheduler.registered_task_count() == 0

	log(title("Cancel the wait task from another thread"))
	f = a.scheduler.schedule_task(a.async_method_wait, 1)
	assert a.scheduler.registered_task_count() == 1

	thread = threading.Thread(target=cancel_tasks_job)
	thread.start()
	for i in range(3):
		sleep(0.2)
	assert a.scheduler.registered_task_count() == 0
	thread.join()

	log(title("Complete tasks in parallel"))
	f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=2)
	assert a.scheduler.registered_task_count() == 1

	thread = threading.Thread(target=run_tasks_job)
	thread.start()
	sleep(0.1)
	run_tasks_job()
	thread.join()

	log(title("Cancel from another thread"))
	f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=3)
	thread = threading.Thread(target=cancel_tasks_job)
	thread.start()
	run_tasks_job()
	thread.join()

	log(title("Wait future"))
	f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=0.6)
	assert a.scheduler.registered_task_count() == 1
	a.scheduler.wait(f)

	log(title("Cancel another thread and wait"))
	f = a.scheduler.schedule_task(a.async_method_sleep, 1, sleep_time=3)
	thread = threading.Thread(target=cancel_tasks_job)
	thread.start()
	a.scheduler.wait_all_tasks()
	thread.join()

	a.update(1)
	

def test():
	log(title("Task Scheduler test"))
	wait_tasks_test()
	log(title("Task Scheduler test completed"))

run()