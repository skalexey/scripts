from utils.log.logger import Logger

log = Logger()
a = 2
b = a + (1 if a == 1 else 0)
log.info(f"b: {b}")