# Allow calls like this: set_log_level(LogLevel.DEBUG)

log_level = 0

class LogLevel:
	VERBOSE = 0
	DEBUG = 1
	INFO = 2
	WARNING = 3
	ERROR = 4
	CRITICAL = 5

def set_log_level(level):
	print(f"Setting log level to {level}")
	global log_level
	log_level = level

def log(level, message):
	if level >= log_level:
		print(message)

def print_debug(message):
	log(LogLevel.DEBUG, message)

def print_info(message):
	log(LogLevel.INFO, message)

def print_warning(message):
	log(LogLevel.WARNING, message)

def print_error(message):
	log(LogLevel.ERROR, message)

def print_critical(message):
	log(LogLevel.CRITICAL, message)

def print_verbose(message):
	log(LogLevel.VERBOSE, message)
