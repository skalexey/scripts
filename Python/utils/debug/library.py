from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.context import GlobalContext


def is_debug():
	attr = getattr(GlobalContext, "is_live", None)
	return (attr or False) is False

def wrap_debug_lock(lock, timeout=None, *args, **kwargs):
	if is_debug():
		_lock = ParameterizedLock(lock, except_on_timeout=True)
		_timeout = timeout if timeout is not None else 3
		_lock.set_constant_args(_timeout, *args, **kwargs)
	else:
		_lock = lock
	return _lock
