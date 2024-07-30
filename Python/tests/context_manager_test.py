from test import *

from utils.lang import safe_enter


def context_manager_test():
	enter_called = None
	exit_called = None

	def exception_test():
		class TestContextManager:
			def __init__(self):
				nonlocal enter_called, exit_called
				enter_called = None
				exit_called = None

			def __enter__(self):
				nonlocal enter_called
				log(utils.method.msg_kw())
				enter_called = True
				return self
			
			def __exit__(self, exc_type, exc_value, traceback):
				nonlocal exit_called
				log(utils.method.msg_kw())
				exit_called = True

		
		with TestContextManager() as cm:
			log(utils.method.msg_kw())
			assert enter_called
			assert not exit_called
		
		assert enter_called
		assert exit_called


		def f(cm):
			log(utils.method.msg_kw())
			try:
				with cm:
					assert enter_called
					assert not exit_called
					raise RuntimeError()
			except RuntimeError:
				log(utils.function.msg_kw("Caught exception"))

		f(TestContextManager())
		assert enter_called
		assert exit_called


		class TestContextManagerExceptionInEnter(TestContextManager):
			def __enter__(self):
				super().__enter__()
				raise RuntimeError()
			
		class TestContextManagerExceptionInEnterSafe(TestContextManagerExceptionInEnter):
			@safe_enter
			def __enter__(self):
				super().__enter__()
			

		f(TestContextManagerExceptionInEnter())
		assert enter_called
		assert not exit_called

		f(TestContextManagerExceptionInEnterSafe())
		assert enter_called
		assert exit_called
		
	
	exception_test()


def test():
	log(title("Context Manager Test"))
	context_manager_test()
	log(title("End of Context Manager Test"))

run()
