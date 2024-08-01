import asyncio
import concurrent.futures


def get_event_loop():
	try:
		loop = asyncio.get_event_loop()
	except RuntimeError:
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
	return loop

def result(task_or_future):
	if task_or_future.cancelled():
		return asyncio.CancelledError()
	if task_or_future.done():
		return task_or_future.exception() or task_or_future.result()
	return task_or_future.get_loop().run_until_complete(task_or_future)

def task(coro, loop=None):
	if isinstance(coro, asyncio.Task):
		return coro
	_loop = loop or get_event_loop()
	tasks = asyncio.all_tasks(_loop)
	for task in tasks:
		if task._coro == coro:
			return task
	return None

# Works only in a running loop.
def create_task_threadsafe(loop, coro, loop_lock, on_done=None):
	timeout = 1
	future = concurrent.futures.Future()
	if on_done is not None:
		future.add_done_callback(on_done)

	def create_task():
		task = loop.create_task(coro)
		future.set_result(task)

	loop.call_soon_threadsafe(create_task)

	def get_result():
		if not loop.is_running():
			with loop_lock:
				loop.run_until_complete(asyncio.sleep(0))
		return future.result(1)

	try:
		return get_result()
	except concurrent.futures.TimeoutError:
		return get_result()  # Wait no more than 1 second for just a task creation and try again. Otherwise, consider it as an error, though it can be just abandoned at excactly that moment


def collect_results(tasks_or_futures):
	done, not_done, results = [], [], []
	for task_or_future in tasks_or_futures:
		if task_or_future.done():
			done.append(task_or_future)
			results.append(result(task_or_future))
		else:
			not_done.append(task_or_future)
	return results, done, not_done 
