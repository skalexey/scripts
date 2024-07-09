from utils.log.logger import Logger

log = Logger()

def verify(condition, message):
	if not condition:
		msg = f"Verification failed: {message}"
		log.error(msg)
		raise Exception(msg)
