import asyncio

class A:
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
	
class MyClass:
	def __init__(self):
		self._tasks = {}
		self._futures_to_functions = {}

	def start_or_continue_async_method(self, async_function):
		result_future = self._futures_to_functions.get(async_function)
		if result_future is None or result_future.done():
			result_future = asyncio.Future()
			task = asyncio.create_task(async_function())
			task.add_done_callback(self._set_result)
			def future_done(future):
				if future.cancelled():
					print(f"Task {async_function.__name__} has been cancelled through the future")
					task.cancel()
			result_future.add_done_callback(future_done)
			self._tasks[task] = (result_future, async_function)
			self._futures_to_functions[async_function] = result_future
		else:
			print("Async method is already running")
		return result_future

	def _set_result(self, task):
		result_future, async_function = self._tasks.pop(task)
		if task.cancelled():
			print(f"Task {async_function.__name__} has been cancelled")
		else:
			assert not result_future.done()
			result_future.set_result(task.result())

	def schedule_task(self, async_function):
		return self.start_or_continue_async_method(async_function)

async def main():
	my_obj = MyClass()
	a = A()
	# Start the async method and get a future
	result_future = my_obj.schedule_task(a.async_method1)

	# Check if the task is done and print the result if it is
	if result_future.done():
		print("Result:", result_future.result())
	else:
		print("Task is not done")

	# Wait for the task to complete and then print the result
	result = await result_future
	print("Result after awaiting:", result)

	print("Calling schedule_task again")
	result_future2 = my_obj.schedule_task(a.async_method2)
	print("Cancel the task 2")
	# my_obj.cancel_task(a.async_method2)
	result_future2.cancel()

	print("Calling schedule_task third time")
	result_future3 = my_obj.schedule_task(a.async_method3)
	result = await result_future3
	print("Result after awaiting third call:", result)

asyncio.run(main())
