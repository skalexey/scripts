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
            result_future.add_done_callback(self._set_result)
            self._tasks[task] = (result_future, async_function)
            self._futures_to_functions[async_function] = result_future
        else:
            print("Async method is already running")
        return result_future

    def _set_result(self, task):
        result_future, async_function = self._tasks[task]
        if task.cancelled():
            result_future.set_exception(asyncio.CancelledError())
        elif task.exception() is not None:
            result_future.set_exception(task.exception())
        else:
            result_future.set_result(task.result())

    def get_result(self, async_function):
        return self.start_or_continue_async_method(async_function)

async def main():
    my_obj = MyClass()
    a = A()
    # Start the async method and get a future
    result_future = my_obj.get_result(a.async_method1)

    # Check if the task is done and print the result if it is
    if result_future.done():
        print("Result:", result_future.result())
    else:
        print("Task is not done")

    # Wait for the task to complete and then print the result
    result = await result_future
    print("Result after awaiting:", result)

    print("Calling get_result again")
    result_future2 = my_obj.get_result(a.async_method2)
    result = await result_future2
    print("Result after awaiting second call:", result)

asyncio.run(main())
