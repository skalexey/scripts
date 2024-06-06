import sys
from utils.function_task_scheduler import *

class A(FunctionTaskScheduler):
	async def async_method1(self):
		print("Task 1 started")
		await asyncio.sleep(1)
		print("Task 1 completed")
		return "Success 1"

	async def async_method2(self):
		print("Task 2 started")
		await asyncio.sleep(1)
		print("Task 2 completed")
		return "Success 2"

	async def async_method3(self):
		print("Task 3 started")
		await asyncio.sleep(1)
		print("Task 3 completed")
		return "Success 3"

	async def parallel_test(self):
		result_future = self.schedule_task(self.async_method1)
		result_future = self.schedule_task(self.async_method2)
		result_future = self.schedule_task(self.async_method3)
		await asyncio.sleep(4)

	async def queue_test(self):
		result_future = self.schedule_task(self.async_method1, 0)
		result_future = self.schedule_task(self.async_method1, 0)
		result_future = self.schedule_task(self.async_method1, 0)
		result_future = self.schedule_task(self.async_method2, 1)
		result_future = self.schedule_task(self.async_method2, 1)
		result_future = self.schedule_task(self.async_method2, 1)
		await asyncio.sleep(5)

	async def test(self):
		await self.parallel_test()

async def main():
	a = A()

	# Call a method that has a name provided in an argument
	if len(sys.argv) < 2:
		await a.test()
	else:
		arg1 = sys.argv[1]
		function_to_call = getattr(a, arg1)
		await function_to_call()
	# await a.test()
	# await a.queue_test()

asyncio.run(main())