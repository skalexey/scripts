import sys
import threading
from time import sleep, time

from utils.context import GlobalContext

GlobalContext.is_live = False
import utils.debug
import utils.debug.debug_detector
import utils.function
import utils.inspect_utils as inspect_utils
import utils.lang
import utils.log
import utils.profile.profiler
import utils.text
from utils.log.logger import Logger, LogLevel

log = Logger()
# TODO: it makes infinite recursion in Subscription.notify
# log_files = utils.log.redirect_to_file_levels(LogLevel.VERBOSE, LogLevel.DEBUG, LogLevel.INFO, LogLevel.ATTENTION)
log_server_port = 36912
utils.log.start_server(log_server_port, LogLevel.VERBOSE, LogLevel.DEBUG, LogLevel.INFO, LogLevel.ATTENTION)
utils.log.redirect_to_server(f"localhost:{log_server_port}")
sleep(1)
profiler = utils.profile.profiler.TimeProfiler()
profiler.set_print_function(log.log)

class LogAddition:
	def __str__(self):
		return f"[{threading.current_thread().name}] "

utils.log.set_global_addition(LogAddition())

def title(text):
	return utils.text.title(text, "=", 60)

class TimeoutException(Exception):
	pass

def timeout(seconds=10):
	def decorator(func):
		def wrapper(*args, **kwargs):
			# This function will run in a separate thread
			is_running = True
			start_time = time()
			elapsed_time = 0
			def target():
				nonlocal is_running, start_time, elapsed_time
				while is_running:
					dt = time() - start_time
					debug_timespan = utils.debug.debug_detector.debug_timespan(func)
					dt -= debug_timespan
					elapsed_time += dt
					if elapsed_time >= seconds:
						raise TimeoutException(f"Test timed out after {seconds} seconds")
					sleep(0.1)

			result = [None, None]
			thread = threading.Thread(target=target)
			thread.start()
			try:
				result[0] = func(*args, **kwargs)
			except Exception as e:
				result[1] = e
			is_running = False
			thread.join()
			if result[1]:
				raise result[1]
			return result[0]
		return wrapper
	return decorator


# Define the test function in your script

class AssertException(Exception):
	def __init__(self, exception):
		self.exception = exception

	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None:
			raise AssertionError(f"Expected exception {self.exception} not raised")
		if not utils.lang.compare_exceptions(self.exception, exc_val):
			raise AssertionError(f"Expected '{self.exception!r}', got '{exc_val!r}'")
		return True

def run():
	function_name = sys.argv[1] if len(sys.argv) > 1 else 'test'
	user_frame = inspect_utils.user_frame()
	# Get the caller's globals from the frame
	function_to_call = user_frame.f_globals[function_name]
	function_to_call()

def assert_exception(expr, result=True):
	ex = None
	try:
		_globals, _locals = inspect_utils.user_globals_locals()
		log(utils.function.msg_v())
		exec(expr, _globals, _locals)
	except Exception as e:
		ex = e
		log(f"Exception caught: '{e}'")
	if result:
		assert ex is not None, f"Expected exception for '{expr}'"
	else:
		assert ex is None, f"Unexpected exception for '{expr}'"

def log_if_true(flag, msg):
	if flag:
		log(msg)
