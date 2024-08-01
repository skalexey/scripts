import utils.function
from utils.log import log_error


def verify(condition, error):
	if not condition:
		msg = utils.function.msg(f"Verification failed: {error}")
		log_error(msg)
		raise error if isinstance(error, BaseException) else Exception(msg)
