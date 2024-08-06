import concurrent.futures
import threading


def do_async(func, *args, **kwargs):
	future = concurrent.futures.Future()

	def job(*args, **kwargs):
		result = None
		try:
			result = func(*args, **kwargs)
		finally:
			future.set_result(result)

	thread = threading.Thread(target=job, args=args, kwargs=kwargs)
	thread.start()
	return future
