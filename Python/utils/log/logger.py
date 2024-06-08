import inspect
import os
from enum import IntEnum


class LogLevel(IntEnum):
	VERBOSE = 0
	DEBUG = 1
	INFO = 2
	WARNING = 3
	ERROR = 4
	CRITICAL = 5
	PRINT = 6

	def sign(level):
		level_str = level.name
		return level_str[0]

	@classmethod
	def items(cls):
		return cls.__members__.items()

	@classmethod
	def values(cls):
		return cls.__members__.values()

	@classmethod
	def keys(cls):
		return cls.__members__.keys()

class Logger:
	def __init__(self, title=None, title_stack_level=1):
		self.log_level = 0
		# Take the caller script name from the stack
		self.log_title = title if title is not None else os.path.splitext(os.path.basename(inspect.stack()[title_stack_level].filename))[0]

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
			# Print the log level,time (hour, minute, second, and microsecond), and the message
			from datetime import datetime
			now = datetime.now()
			current_time = now.strftime("%H:%M:%S.%f")
			level_sign = LogLevel.sign(level)
			level_prefix = f"[{level_sign}] " if level_sign is not None else "    "
			log_title_addition = f"[{self.log_title}]: " if self.log_title is not None else ""
			msg = f"{level_prefix}[{current_time}] {log_title_addition}{message}"
			print(msg)
			return msg, message, level, self.log_title, current_time

	def _exec(self, expression, globals=None, locals=None):
		try:
			result = exec(expression, globals, locals)
			return result
		except Exception as e:
			self.log_error(f"Error evaluating expression: '{expression}'. Exception: '{e}'")
			return None

	def log_expr(self, expression, globals = None, locals=None):
		# Take the globals from the stack
		if globals is None or locals is None:
			frame = inspect.stack()[1].frame
			globals_to_take = frame.f_globals
			locals_to_take = frame.f_locals
		else:
			globals_to_take = globals
			locals_to_take = locals
		self.log(expression)
		result = self._exec(expression, globals_to_take, locals_to_take)
		return result
	
	def log_expr_val(self, expression, globals, locals):
		result = self._exec(expression, globals, locals)
		self.log(result)
		return result

	def log_expr_and_val(self, expression, globals = None, locals=None):
		result = self._exec(expression, globals, locals)
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