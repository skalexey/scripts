from utils.log import *

logger = Logger()
a = 2
b = a + (1 if a == 1 else 0)
logger.log_info(f"b: {b}")