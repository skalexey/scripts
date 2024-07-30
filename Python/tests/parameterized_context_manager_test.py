import unittest
from test import *
from unittest.mock import Mock, patch

import utils.debug
import utils.debug.debug_detector
from utils.parameterized_context_manager import ParameterizedContextManager


class TestParameterizedContextManager(unittest.TestCase):
	def setUp(self):
		self.obj = Mock()
		self.on_enter = Mock(return_value=True)
		self.on_exit_by_condition = Mock()
		self.context_manager = ParameterizedContextManager(self.obj, self.on_enter, self.on_exit_by_condition)

	def test_on_enter_result(self):
		with self.context_manager() as state:
			self.assertTrue(state.enter_result())

	def test_on_enter_call(self):
		with self.context_manager(1, 2, key='value'):
			self.on_enter.assert_called_once_with(self.obj, 1, 2, key='value')

	def test_constant_args(self):
		self.context_manager.set_constant_args(1, 2, key='value')
		with self.context_manager as state:
			self.on_enter.assert_called_once_with(self.obj, 1, 2, key='value')
			self.assertTrue(state.enter_result())

		self.on_enter.reset_mock()

		with self.context_manager as state:
			self.on_enter.assert_called_once_with(self.obj, 1, 2, key='value')
			self.assertTrue(state.enter_result())

		# State keeps the last values
		self.assertTrue(state.enter_result())
		self.assertTrue(len(self.context_manager._thread_local.state_stack) == 0)

		self.on_enter.reset_mock()

	def test_exit_by_condition_call(self):
		with self.context_manager(1, 2, key='value') as state:
			self.assertTrue(state.enter_result())
		self.on_exit_by_condition.assert_called_once_with(self.obj)

	def test_exception(self):
		try:
			with self.context_manager() as state:
				self.assertTrue(state.enter_result())
				raise RuntimeError("Test exception")
		except RuntimeError:
			pass

def parameterized_context_manager_test():
	unittest.main()

def test():
	log(title("Parameterized Context Manager Test"))
	parameterized_context_manager_test()
	log(title("End of Parameterized Context Manager Test"))

run()
