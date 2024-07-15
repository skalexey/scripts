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

	t = threading.Thread(target=job, args=args, kwargs=kwargs)
	t.start()
	return future
