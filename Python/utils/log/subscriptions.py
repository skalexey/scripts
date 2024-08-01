from utils.log.logger import LogLevel
from utils.log.server import LogServer
from utils.subscription import Subscription

g_on_log_level = [Subscription() for _ in range(len(LogLevel))]
g_on_log = Subscription()

# Generate global subscriptions g_on_<log_level> for each log level and override the log_<log_level> methods to notify the subscription
def _init():
	_globals = globals()
	for key, value in LogLevel.items():
		level_name = key.lower()
		assert f"g_on_log_{level_name}" not in _globals
		subscription = Subscription()
		_globals[f"g_on_log_{level_name}"] = subscription
		g_on_log_level[value] = subscription
	# Override the log method to notify a particular subscription
	base_log = LogServer.on_log
	def log(self, packet):
		_log = base_log(self, packet)
		g_on_log_level[packet.level.value].notify(_log)
		g_on_log.notify(_log)
		return _log
	LogServer.on_log = log

_init()
