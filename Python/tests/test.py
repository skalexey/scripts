import inspect
import sys

import utils.profile.profiler
import utils.text
from utils.log.logger import *
from utils.subscription import *

# Caller script name from the stack
log = Logger(title_stack_level=2)
profiler = utils.profile.profiler.TimeProfiler()
profiler.set_print_function(log.log)

def title(text):
	return utils.text.title(text, "=", 60)

# Define the test function in your script

def run():
	function_name = sys.argv[1] if len(sys.argv) > 1 else 'test'
	caller_frame = inspect.stack()[1].frame

	# Get the caller's globals from the frame
	caller_globals = caller_frame.f_globals
	function_to_call = caller_globals[function_name]
	function_to_call()
