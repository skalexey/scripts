from utils.context import GlobalContext
from utils.debug.debug_detector import DebugDetector

debug_detector = DebugDetector()

def is_debug():
	return not GlobalContext.is_live

def debug_timespan(checker):
	if is_debug():
		return debug_detector.grab_last_debug_timespan(checker)
	return 0
