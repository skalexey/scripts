import utils.method
from utils.concurrency.abstract_lock import AbstractLock
from utils.log.logger import Logger
from utils.parameterized_context_manager import (
    ParameterizedContextManagerBase,
    ParameterizedContextManagerState,
)

log = Logger()


class ParameterizedLockState(ParameterizedContextManagerState):
	@property
	def lock(self):
		return self.cm

	def acquired(self):
		return self.enter_result()


class ParameterizedLock(ParameterizedContextManagerBase, AbstractLock):
	def __init__(self, lock, except_on_timeout=None, *args, **kwargs):
		super().__init__(lock, *args, **kwargs)
		self._except_on_timeout = RuntimeError("Failed to acquire the lock in time") if except_on_timeout is True else except_on_timeout
		self._locked = False

	def acquire(self, *args, **kwargs):
		state = self._create_state(*args, **kwargs)
		self._enter_state(state)
		acquired = state.acquired()
		self._locked = acquired
		return acquired
	
	def release(self):
		state = self.state
		if state is None:
			raise RuntimeError(utils.method.msg_kw("Lock is not acquired"))
		if state.acquired():
			self._locked = False
		self._exit_state(state=state)

	def acquired(self):
		state = self.state
		return state and state.acquired()
	
	def locked(self):
		return self._locked

	def _create_state(self, *args, **kwargs):
		return ParameterizedLockState(self, *args, **kwargs)

	def _enter(self, *args, timeout=-1, **kwargs):
		# log.debug(utils.method.msg_kw(f"Acquiring lock '{self._obj}'"))
		result = self._obj.acquire(*args, timeout=timeout, **kwargs)
		if not result:
			if timeout >= 0:
				if self._except_on_timeout is not None:
					if self._except_on_timeout is True:
						raise RuntimeError(f"Failed to enter '{self._obj}' in time {timeout}")
					raise self._except_on_timeout
		return result

	def _exit_by_condition(self, exc_type, exc_value, traceback):
		# log.debug(utils.method.msg(f"Releasing lock '{self._obj}'"))
		self._obj.release()
		# log.debug(utils.method.msg(f"Released lock '{self._obj}'"))
