import threading
import weakref
from abc import ABC, abstractmethod

import utils.method
from utils.lang import NoValue, safe_enter
from utils.log.logger import Logger

log = Logger()


class ParameterizedContextManagerState():
	def __init__(self, context_manager, *args, **kwargs):
		super().__init__()
		self._cm = weakref.ref(context_manager)
		self.on_enter_result = NoValue
		self.args = args
		self.kwargs = kwargs

	@property
	def cm(self):
		return self._cm()

	@safe_enter
	def __enter__(self):
		self.cm._on_state_enter(self)
		self.on_enter_result = self.cm._enter(*self.args, **self.kwargs)
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		result = self.cm._on_state_exit(exc_type, exc_value, traceback, self)
		self.cm._exit(self, exc_type, exc_value, traceback)
		# self.on_enter_result = NoValue
		return result

	def enter_result(self):
		return self.on_enter_result

	def __repr__(self):
		return f"{self.__class__.__name__}(cm={self.cm}, on_enter_result={self.on_enter_result}, args={self.args}, kwargs={self.kwargs})"

class ParameterizedContextManagerBase(ABC):
	def __init__(self, obj, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._obj = obj
		self._exit_cb_condition = True
		self._constant_args = None
		self._constant_kwargs = None
		self._thread_local = threading.local()
		self._thread_local.state_stack = []

	@property
	def state(self):
		stack = getattr(self._thread_local, "state_stack", None)
		if not stack:
			return None
		return self._thread_local.state_stack[-1]

	def __getattr__(self, name):
		return getattr(self._obj, name)

	def __call__(self, *args, **kwargs):
		return self._create_state(*args, **kwargs)

	def _create_state(self, *args, **kwargs):
		return ParameterizedContextManagerState(self, *args, **kwargs)

	# Ordinary enter without parameters is also possible. It is done through this __enter__() method.
	# It can use constant arguments set by set_constant_args() method.
	@safe_enter
	def __enter__(self):
		if self._constant_args is not None:
			args = self._constant_args
			kwargs = self._constant_kwargs
		else:
			args = ()
			kwargs = {}
		state = self._create_state(*args, **kwargs)
		return self._enter_state(state)

	def __exit__(self, exc_type, exc_value, traceback):
		self._exit_state(exc_type, exc_value, traceback)

	def _check_state_to_exit(self, state, current_state):
		if state is not None:
			if state is not current_state:
				raise RuntimeError(f"Invalid state to exit: {state}")
		return True

	def _on_state_exit(self, exc_type=None, exc_value=None, traceback=None, state=None): # state is optional for validation that it is the current state
		current_state = self._thread_local.state_stack.pop()
		self._check_state_to_exit(state, current_state)
		return None

	def _exit_state(self, exc_type=None, exc_value=None, traceback=None, state=None):
		curret_state = self.state
		result = self._check_state_to_exit(state, curret_state)
		curret_state.__exit__(exc_type, exc_value, traceback)
		return result
		
	def _enter_state(self, state):
		return state.__enter__()

	def _on_state_enter(self, state):
		state_stack = getattr(self._thread_local, "state_stack", None)
		if state_stack is None:
			self._thread_local.state_stack = state_stack = []
		state_stack.append(state)

	@abstractmethod
	def _enter(self, *args, **kwargs): # -> any
		pass

	def _exit(self, state, exc_type, exc_value, traceback):
		if state.on_enter_result == self._exit_cb_condition:
			return self._exit_by_condition(exc_type, exc_value, traceback)
		return None

	def set_constant_args(self, *args, **kwargs):
		self._constant_args = args
		self._constant_kwargs = kwargs

	def reset_constant_args(self):
		self._constant_args = None
		self._constant_kwargs = None

	
	@abstractmethod
	def _exit_by_condition(self, exc_type, exc_value, traceback):
		pass
			

class ParameterizedContextManager(ParameterizedContextManagerBase):
	def __init__(self, obj, on_enter, on_exit_by_condition, exit_cb_condition=True, *args, **kwargs):
		super().__init__(obj, *args, **kwargs)
		self._exit_cb_condition = exit_cb_condition
		self._on_enter_cb = on_enter
		self._exit_by_condition_cb = on_exit_by_condition

	def _enter(self, *args, **kwargs):
		return self._on_enter_cb(self._obj, *args, **kwargs)

	def _exit_by_condition(self, exc_type, exc_value, traceback):
		return self._exit_by_condition_cb(self._obj)
