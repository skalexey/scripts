import inspect
import os
import threading

import utils  # Lazy import
import utils.inspect_utils as inspect_utils
from utils.log.log import LogLevel
from utils.log.log import log as _log


class Logger:
	log_addition = None

	def __init__(self, title=None, title_stack_level=1):
		super().__init__()
		self.log_level = 0
		# Take the caller script name from the stack
		self.log_title = title or os.path.splitext(os.path.basename(inspect.stack()[title_stack_level].filename))[0]
		self._on_log = None # Allocated on demand through on_log property
		self.file = None

	@property
	def on_log(self):
		if self._on_log is None:
			self._on_log = utils.subscription.Subscription()
		return self._on_log

	def set_log_title(self, title):
		self.log_title = title

	def set_log_level(self, level):
		self.log(f"Setting log level to {level}")
		self.log_level = level

	def __call__(self, message, level=LogLevel.PRINT):
		self.log(message, level)

	# Variadic arguments
	def log(self, message, level=LogLevel.PRINT):
		if level >= self.log_level:
			result = _log(message, level, self.log_title, self.log_addition)
			if self._on_log:
				self._on_log(result)
			return result

	def redirect_to_file(self, fpath=None, level=None, *args, **kwargs):
		self.file = utils.log.redirect_to_file(fpath, level, self.on_log, *args, **kwargs)
		return self.file

	def _exec(self, expression, globals=None, locals=None):
		try:
			_globals, _locals = inspect_utils.user_globals_locals(self, globals, locals)
			exec(expression, _globals, _locals)
		except Exception as e:
			self.error(f"Error executing expression: '{expression}': '{e}'")
		
	def _eval(self, expression, globals=None, locals=None):
		try:
			_globals, _locals = inspect_utils.user_globals_locals(self, globals, locals)
			result = eval(expression, _globals, _locals)
			return result
		except Exception as e:
			self.error(f"Error evaluating expression: '{expression}': '{e}'")
			return None

	def expr(self, expression, globals=None, locals=None):
		self.log(expression)
		self._exec(expression, globals, locals)
	
	def expr_val(self, expression, globals, locals):
		result = self._eval(expression, globals, locals)
		self.log(result)
		return result

	def expr_and_val(self, expression, globals=None, locals=None):
		result = self._eval(expression, globals, locals)
		self.log(f"{expression}: {result}")
		return result

# Generate log_<level_name> functions
def _init():
	def log_fn(level_name, level_value):
		def log_level(self, msg):
			result = self.log(msg, level_value)
			# result: (msg, message, level, self.log_title, current_time)
			return result
		return log_level
	for key, value in LogLevel.items():
		name = key.lower()
		setattr(Logger, f"{name}", log_fn(name, value))

_init()
# Discouraged global monolite interface.
# Prefer crating a logger object in the calling module.
loggers = {}

def logger():
	import inspect

	# frame = inspect.currentframe().f_back
	# module = inspect.getmodule(frame)
	stack = inspect.stack()
	# Find the first module that doesn't end with log.py
	# This is the module that called the logger
	calling_module_name = None
	for i in range(1, len(stack)):
		if not stack[i].filename.endswith("log.py"):
			calling_module_name = stack[i].filename
			break
	if calling_module_name is None:
		raise ValueError("Could not find calling module")
	if calling_module_name not in loggers:
		loggers[calling_module_name] = Logger()
	return loggers[calling_module_name]

def set_log_title(title):
	logger().set_log_title(title)

def set_log_level(level):
	logger().set_log_level(level)

def log(message, level=LogLevel.PRINT):
	logger().log(message, level=LogLevel.PRINT)

def log_debug(message):
	logger().log_debug(message)

def log_info(message):
	logger().log_info(message)

def log_warning(message):
	logger().log_warning(message)

def log_error(message):
	logger().log_error(message)

def log_critical(message):
	logger().log_critical(message)

def log_verbose(message):
	logger().log_verbose(message)
