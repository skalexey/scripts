import inspect
import os


class LogLevel:
	VERBOSE = 0
	DEBUG = 1
	INFO = 2
	WARNING = 3
	ERROR = 4
	CRITICAL = 5
	PRINT = 6

	def sign(level):
		if level == LogLevel.PRINT:
			return None
		if level == LogLevel.PRINT:
			return "P"
		if level == LogLevel.VERBOSE:
			return "V"
		if level == LogLevel.DEBUG:
			return "D"
		if level == LogLevel.INFO:
			return "I"
		if level == LogLevel.WARNING:
			return "W"
		if level == LogLevel.ERROR:
			return "E"
		if level == LogLevel.CRITICAL:
			return "C"
		raise ValueError(f"Unknown log level when calling LogLevel.sign({level})")

class Logger:
	def __init__(self, title=None):
		self.log_level = 0
		# Take the caller script name from the stack
		self.log_title = title if title is not None else os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]

	def set_log_title(self, title):
		self.log_title = title

	def set_log_level(self, level):
		self.log(f"Setting log level to {level}")
		self.log_level = level

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
			print(f"{level_prefix}[{current_time}] {log_title_addition}{message}")

	def log_debug(self, message):
		self.log(message, LogLevel.DEBUG)

	def log_info(self, message):
		self.log(message, LogLevel.INFO)

	def log_warning(self, message):
		self.log(message, LogLevel.WARNING)

	def log_error(self, message):
		self.log(message, LogLevel.ERROR)

	def log_critical(self, message):
		self.log(message, LogLevel.CRITICAL)

	def log_verbose(self, message):
		self.log(message, LogLevel.VERBOSE)

	def log_expr(self, expression, globals = None, locals=None):
		self.log(expression)
		result = eval(expression, globals, locals)
		return result
	
	def log_expr_val(self, expression, globals, locals):
		result = eval(expression, globals, locals)
		self.log(result)
		return result

	def log_expr_and_val(self, expression, globals = None, locals=None):
		result = eval(expression, globals, locals)
		self.log(f"{expression}: {result}")

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
