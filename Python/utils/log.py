# Allow calls like this: set_log_level(LogLevel.DEBUG)

log_level = 0

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

def set_log_level(level):
	print(f"Setting log level to {level}")
	global log_level
	log_level = level

# Variadic arguments
def log(message, level=LogLevel.PRINT):
	if level >= log_level:
		# Print the log level,time (hour, minute, second, and microsecond), and the message
		from datetime import datetime
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S.%f")
		level_sign = LogLevel.sign(level)
		level_prefix = f"[{level_sign}] " if level_sign is not None else "    "
		print(f"{level_prefix}[{current_time}] {message}")

def log_debug(message):
	log(message, LogLevel.DEBUG)

def log_info(message):
	log(message, LogLevel.INFO)

def log_warning(message):
	log(message, LogLevel.WARNING)

def log_error(message):
	log(message, LogLevel.ERROR)

def log_critical(message):
	log(message, LogLevel.CRITICAL)

def log_verbose(message):
	log(message, LogLevel.VERBOSE)
