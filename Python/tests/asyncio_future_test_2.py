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
		self._functions_to_tasks = {}

	class TaskInfo:
		def __init__(self, result_future, task, function):
			self.future = result_future
			self.task = task
			self.function = function

	def schedule_task(self, async_function):
		function_info = self._functions_to_tasks.get(async_function)
		if function_info is None or function_info.future.done():
			result_future = asyncio.Future()
			task = asyncio.create_task(async_function())
			def future_done(future):
				if task.cancelled():
					print(f"Task {async_function.__name__} has been cancelled")
					result_future.cancel()
				else:
					result_future.set_result(task.result())
			task.add_done_callback(self._set_result)
			task_info = self.TaskInfo(result_future, task, async_function)
			result_future.add_done_callback(future_done)
			self._tasks[task] = task_info
			self._functions_to_tasks[async_function] = task_info
		else:
			print("Async method is already running")
		return result_future
	
	# def cancel_task(self, async_function):
	# 	task_info = self._functions_to_tasks.get(async_function)
	# 	if task_info is not None and not task_info.future.done():
	# 		task_info.task.cancel()
	# 		del self._functions_to_tasks[async_function]
	# 		del self._tasks[task_info.task]
	# 		print("Task cancelled")

	def _set_result(self, task):
		if task.cancelled():
			print(f"Task {task} has been cancelled")
			task_info = self._tasks.pop(task)
			task_info.future.cancel()
			return
		task_info = self._tasks[task]
		if task_info.future.cancelled():
			print("Future already cancelled")
			return
		if task_info.future.done():
			print("Future done returns True")
			return
		assert not task_info.future.done()
		task_info.future.set_result(task.result())

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

	print("Calling get_result again")
	result_future2 = my_obj.schedule_task(a.async_method2)
	print("Cancel the task 2")
	# my_obj.cancel_task(a.async_method2)
	result_future2.cancel()

	print("Calling get_result third time")
	result_future3 = my_obj.schedule_task(a.async_method3)
	result = await result_future3
	print("Result after awaiting third call:", result)

asyncio.run(main())
