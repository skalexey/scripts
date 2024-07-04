import inspect
import sys

import utils.function
import utils.inspect_utils as inspect_utils
import utils.profile.profiler
import utils.text
from utils.log.logger import Logger
from utils.subscription import *

# Caller script name from the stack
log = Logger()
profiler = utils.profile.profiler.TimeProfiler()
profiler.set_print_function(log.log)

def title(text):
	return utils.text.title(text, "=", 60)

# Define the test function in your script

def run():
	function_name = sys.argv[1] if len(sys.argv) > 1 else 'test'
	user_frame = inspect_utils.user_frame()
	# Get the caller's globals from the frame
	function_to_call = user_frame.f_globals[function_name]
	function_to_call()
