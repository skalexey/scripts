import sys

import utils.profiler
import utils.text
from utils.log.logger import *
from utils.task_scheduler import *

log = Logger()
profiler = utils.profiler.TimeProfiler()
profiler.set_print_function(log.log)

def title(text):
	return utils.text.title(text, "=", 60)
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

def main():
	a = A()

	# Call a method that has a name provided in an argument
	if len(sys.argv) < 2:
		a.test()
	else:
		arg1 = sys.argv[1]
		function_to_call = getattr(a, arg1)
		function_to_call()
	# await a.test()
	# await a.queue_test()

main()