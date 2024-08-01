from utils.context import GlobalContext


def is_debug():
	attr = getattr(GlobalContext, "is_live", None)
	return (attr or False) is False
