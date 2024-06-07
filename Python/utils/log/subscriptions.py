from utils.log.logger import *
from utils.subscription import *

g_on_log_level = [Subscription() for _ in range(len(LogLevel))]

# Generate global subscriptions g_on_<log_level> for each log level and override the log_<log_level> methods to notify the subscription
def _init():
	# def gen_log_level_fn(level_name, level_value, subscription):
	# 	log_level_base = getattr(Logger, f"log_{level_name}")
	# 	def fn(self, msg):
	# 		result = log_level_base(self, msg)
	# 		subscription.notify(result)
	# 		return result
	# 	return fn
	_globals = globals()
	for key, value in LogLevel.items():
		level_name = key.lower()
		assert(f"g_on_log_{level_name}" not in _globals)
		subscription = Subscription()
		_globals[f"g_on_log_{level_name}"] = subscription
		g_on_log_level[value] = subscription
		# fn = gen_log_fn(level_name, value, subscription)
		# setattr(Logger, f"log_{level_name}", fn)
	# Override the log method to notify a particular subscription
	base_log = Logger.log
	def log(self, msg, level=LogLevel.PRINT):
		result = base_log(self, msg, level)
		g_on_log_level[level.value].notify(result)
		return result
	Logger.log = log
_init()
	