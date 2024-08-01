import inspect
import os

import utils  # Lazy import for less important modules
import utils.inspect_utils as inspect_utils
import utils.log
from utils.log import Log, LogLevel, TitleAddition, _gen_log_funcs
from utils.log import log as _g_log
from utils.log import log_to_server


class Logger:
	log_addition = None

	def __init__(self, title=None, title_stack_level=1):
		super().__init__()
		self.log_level = 0
		self.log_addition = None
		self.connection = None
		# Take the caller script name from the stack
		self.set_log_title(title or os.path.splitext(os.path.basename(inspect.stack()[title_stack_level].filename))[0])
		self._on_log = None # Allocated on demand through on_log property
		self.file = None
		self._log = _g_log

	@property
	def on_log(self):
		if self._on_log is None:
			self._on_log = utils.subscription.Subscription()
		return self._on_log

	def set_log_title(self, title):
		self.log_title = title
		if self.log_addition is not None:
			if not isinstance(self.log_addition, TitleAddition):
				raise ValueError("Cannot set log title when log addition is not empty")
		self.log_addition = TitleAddition(title)

	def set_log_level(self, level):
		self.log(f"Setting log level to {level}")
		self.log_level = level

	def __call__(self, *args, **kwargs):
		self.log(*args, **kwargs)

	# Variadic arguments
	def log(self, message, level=LogLevel.PRINT, addition=None):
		if level >= self.log_level:
			args = (message, level, self.log_title, (str(self.log_addition or "") + str(addition or "")) or None)
			result = self._log(*args)
			if self._on_log:
				self._on_log(result)
			return result

	def redirect_to_file(self, fpath=None, level=None, *args, **kwargs):
		utils.live.verify(self.file is None, "File already opened for writing")
		self.file = utils.log.redirect_to_file(fpath, level, self.on_log, *args, **kwargs)
		return self.file
	
	def close_connection(self):
		if self.connection:
			self.on_log.unsubscribe(self.connection)
			self.connection.close()
			self.connection = None
	
	def redirect_to_server(self, address):
		utils.live.verify(self.connection is None, "Connection already established")
		self.connection = utils.log.redirect_to_server(address, self.on_log)
		def log(*args, **kwargs):
			return log_to_server(self.connection, *args, **kwargs)
		self._log = log

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
	funcs = _gen_log_funcs(Logger.log)
	for level_name, func in funcs.items():
		setattr(Logger, f"{level_name}", func)

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
