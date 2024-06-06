import sys
import threading
import time

from utils.asyncio_utils import *
from utils.log import *
from utils.task_scheduler import *

logger = Logger("asyncio_integration_test")

class A(TaskScheduler):
	def __init__(self):
		super().__init__()
		self.last_measurement = None
	
	def time_since_last_measurement(self):
		current_time = time.time()
		if self.last_measurement is not None:
			return current_time - self.last_measurement
		self.last_measurement = current_time
		return 0

	def measure_time(self):
		self.last_measurement = time.time()

	def print_time_since_last_measurement(self):
		# Print seconds + milliseconds
		logger.log(f"Time since last measurement: {self.time_since_last_measurement()}")

	def test(self):
		self.cancel_future_test()
		return
		self.integrity_test()
		self.simple_cancel_test()
		self.cancel_test()
		return
		self.simple_cancel_test()
		self.simple_cancel_test()
		return
		logger.log("Test started")
		f1 = self.schedule_task(self.async_method_1s_1)
		f2 = self.schedule_task(self.async_method_1s_2)
		f3 = self.schedule_task(self.async_method_1s_3)
		# Waiting through tasks
		# loop = utils.asyncio.get_event_loop()
		# for task in self._tasks.copy():
		# 	loop.run_until_complete(task)
		# Waiting through futures
		# for f in [f1, f2, f3]:
		# 	f.get_loop().run_until_complete(f)
		# Higher-level waiting
		self.wait_all_tasks()
		logger.log("Test completed")
		# loop.run_forever()

	def integrity_test(self):
		logger.log("Integrity test started")
		logger.log("Schedule 1st task")
		f1 = self.schedule_task(self.async_method_1s_1)
		assert(len(self._tasks) == 1)
		logger.log("Waiting for 1st task")
		self.measure_time()
		self.wait_all_tasks()
		self.print_time_since_last_measurement()
		assert(len(self._tasks) == 0)
		logger.log("Schedule 2nd task")
		f2 = self.schedule_task(self.async_method_1s_1)
		assert(len(self._tasks) == 1)
		logger.log("Waiting for 2nd task")
		self.measure_time()
		self.wait_all_tasks()
		self.print_time_since_last_measurement()
		assert(len(self._tasks) == 0)
		logger.log("Integrity test completed")

	async def async_method_1s_1(self):
		logger.log("Task 1 started")
		await asyncio.sleep(1)
		logger.log("Task 1 completed")
		return "Success 1"

	async def async_method_1s_2(self):
		logger.log("Task 2 started")
		await asyncio.sleep(1)
		logger.log("Task 2 completed")
		return "Success 2"

	async def async_method_1s_3(self):
		logger.log("Task 3 started")
		await asyncio.sleep(1)
		logger.log("Task 3 completed")
		return "Success 3"
	
	async def async_method_no_wait(self):
		logger.log("Task 4 started")
		logger.log("Task 4 completed")
		return "Success 4"
	
	async def sleep_task(self):
		logger.log("Enter sleep task")
		await asyncio.sleep(3)
		logger.log("Exit sleep task")

	def async_test(self):
		async def test():
			logger.log("Async test started")
			self.schedule_task(self.async_method_1s_1)
			await asyncio.sleep(2)
			logger.log("Async test completed")
		logger.log("Async test started")
		loop = utils.asyncio.get_event_loop()
		loop.run_until_complete(test())
		logger.log("Async test completed")

	def sync_async_test(self):
		logger.log("Sync async test started")
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(self.async_test())
		loop.close()
		logger.log("Sync async test completed")

	def cancel_test(self):
		logger.log("Cancel test started")
		f1 = self.schedule_task(self.async_method_1s_1)
		f2 = self.schedule_task(self.async_method_1s_2)
		f3 = self.schedule_task(self.async_method_1s_3)
		f4 = self.schedule_task(self.async_method_no_wait)
		time.sleep(0.5)
		logger.log("Cancelling all tasks")
		# self.cancel_all_tasks()
		logger.log("Waiting")
		self.measure_time()
		self.wait_all_tasks()
		assert(self.time_since_last_measurement() >= 1)
		self.print_time_since_last_measurement()
		logger.log("Waiting 2")
		self.measure_time()
		self.wait_all_tasks()
		self.print_time_since_last_measurement()
		assert(self.time_since_last_measurement() < 0.01)
		logger.log("Place a task and wait 3rd time")
		assert(len(self._tasks) == 0)
		self.schedule_task(self.async_method_1s_3)
		self.measure_time()
		self.wait_all_tasks()
		self.print_time_since_last_measurement()
		assert(self.time_since_last_measurement() >= 1)
		logger.log("Wait through a future")
		f5 = self.schedule_task(self.async_method_1s_1)
		self.measure_time()
		self.wait(f5)
		self.print_time_since_last_measurement()
		assert(self.time_since_last_measurement() >= 1)
		logger.log("Cancel test completed")
		loop = utils.asyncio_utils.get_event_loop()
		tasks = asyncio.all_tasks(loop)
		assert(len(tasks) == 0)

	def simple_cancel_test(self):
		logger.log("Simple cancel test started")
		f1 = self.schedule_task(self.async_method_1s_1)
		logger.log("Cancelling the task")
		self.cancel_all_tasks()
		logger.log("Waiting")
		self.wait_all_tasks()
		logger.log("Simple cancel test completed")
		assert(len(self._tasks) == 0)
		loop = utils.asyncio_utils.get_event_loop()
		tasks = asyncio.all_tasks(loop)
		assert(len(tasks) == 0)

	def cancel_future_test(self):
		logger.log("Cancel future test started")
		f = self.schedule_task(self.async_method_1s_1)
		f.cancel()
		logger.log("Waiting")
		self.measure_time()
		self.wait_all_tasks()
		self.print_time_since_last_measurement()
		assert(self.time_since_last_measurement() < 0.01)
		# f2 = self.schedule_task(self.async_method_1s_2, 1)
		# self.wait(f2)
		loop = utils.asyncio_utils.get_event_loop()
		tasks = asyncio.all_tasks(loop)
		if len(tasks) > 0:
			logger.log_warning(f"Tasks still exist in the loop after cancelling: {tasks}")
		for task in tasks:
			# Run until complete
			# assert(task.done())
			# assert(task.cancelled())
			if not task.cancelled():
				loop.run_until_complete(task)
		tasks = asyncio.all_tasks(loop)
		assert(len(tasks) == 0)
		logger.log("Cancel future test completed")

def main():
	a = A()
	if len(sys.argv) < 2:
		a.test()
	else:
		arg1 = sys.argv[1]
		function_to_call = getattr(a, arg1)
		function_to_call()

main()