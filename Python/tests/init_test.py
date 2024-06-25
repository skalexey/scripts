from test import *


def init_test():
	class A:
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			mro = self.__class__.mro()
			for m in mro:
				log.debug(utils.function.msg(f"mro: {m}"))

def test():
	log(title("Init Test"))
	init_test()
	log(title("End of Init Test"))

run()
