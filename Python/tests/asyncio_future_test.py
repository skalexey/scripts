import asyncio

class MyClass:
    def __init__(self):
        self._result_future = None

    async def _async_method(self):
        print("Task started")
        await asyncio.sleep(1)
        print("Task completed")
        return "Success"

    def start_or_continue_async_method(self):
        if self._result_future is None or self._result_future.done():
            self._result_future = asyncio.Future()
            task = asyncio.create_task(self._async_method())
            task.add_done_callback(self._set_result)
        else:
            print("Async method is already running")
        return self._result_future

    def _set_result(self, task):
        assert not self._result_future.done()
        self._result_future.set_result(task.result())

    def get_result(self):
        return self.start_or_continue_async_method()

async def main():
    my_obj = MyClass()

    # Start the async method and get a future
    result_future = my_obj.get_result()

    # Check if the task is done and print the result if it is
    if result_future.done():
        print("Result:", result_future.result())
    else:
        print("Task is not done")

    # Wait for the task to complete and then print the result
    result = await result_future
    print("Result after awaiting:", result)

    print("Calling get_result again")
    result_future2 = my_obj.get_result()
    result = await result_future2
    print("Result after awaiting second call:", result)

asyncio.run(main())
