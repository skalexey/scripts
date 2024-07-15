import threading
from datetime import datetime
from enum import IntEnum

log_lock = threading.Lock()


class LogLevel(IntEnum):
	VERBOSE = 0
	LOOP_VERBOSE = 1 # Loop iterations that spam significantly
	LOOP = 2 # Loop iterations
	DEBUG = 3
	INFO = 4
	SUCCESS = 5
	ATTENTION = 6
	WARNING = 7
	ERROR = 8
	CRITICAL = 9
	PRINT = 10

	def sign(level):
		level_str = level.name
		# Find the first letter of each part separated by _
		split = level_str.split("_")
		return "".join([s[0] for s in split])

	@classmethod
	def items(cls):
		return cls.__members__.items()

	@classmethod
	def values(cls):
		return cls.__members__.values()

	@classmethod
	def keys(cls):
		return cls.__members__.keys()
	

# Variadic arguments
def log(message, level=LogLevel.PRINT, log_title=None, log_addition=None):
	# Print the log level,time (hour, minute, second, and microsecond), and the message
	from datetime import datetime
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S.%f")
	level_sign = LogLevel.sign(level)
	level_prefix = f"[{level_sign}] " if level_sign else "    "
	log_title_addition = f"[{log_title}]: " if log_title else ""
	log_addition_str = log_addition or ""
	msg = f"{level_prefix}[{current_time}] {log_addition_str}{log_title_addition}{message}"
	with log_lock:
		print(msg)
	result = (msg, message, level, log_title, current_time)
	return result
