from utils.log.logger import Logger

log = Logger()

def verify(condition, error):
	if not condition:
		msg = f"Verification failed: {error}"
		log.error(msg)
		raise error if isinstance(error, BaseException) else Exception(msg)
