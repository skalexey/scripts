import threading

import utils.method
from utils.concurrency.abstract_lock import AbstractLock
from utils.lang import NoValue, safe_enter
from utils.live import verify
from utils.log.logger import Logger
from utils.parameterized_context_manager import (
    ParameterizedContextManagerBase,
    ParameterizedContextManagerState,
)

log = Logger()


class ParameterizedLockState(ParameterizedContextManagerState):
	def __init__(self, *args, **kwargs):
		assert not args or args[0] is not None
		super().__init__(*args, **kwargs)
		self._owner_thread = threading.current_thread()

	def owner(self):
		assert self._owner_thread.ident == utils.concurrency.lock_owner(self.cm._obj)
		return self._owner_thread.name

	@property
	def lock(self):
		return self.cm

	def acquired(self):
		return self.enter_result()

	# Safe-enter in super().__enter__()
	def __enter__(self):
		super().__enter__()
		return self.acquired()


class ParameterizedLock(ParameterizedContextManagerBase, AbstractLock):
	def __init__(self, lock, except_on_timeout=None, *args, **kwargs):
		super().__init__(lock, *args, **kwargs)
		self._except_on_timeout = except_on_timeout
		self._locked = False
		self._owner = None

	# Override
	def _merge_into_constant_args(self, args, kwargs):
		blocking, timeout = self._decompose_args(*args, **kwargs)[:2] # Arguments are supposed being already validated
		constant_blocking, constant_timeout = self._decompose_args(*self._constant_args, **self._constant_kwargs)[:2]
		_blocking = blocking if blocking is not NoValue else constant_blocking
		_timeout = timeout if timeout is not NoValue else (constant_timeout if _blocking else NoValue)
		_args = []
		_kwargs = {}
		if _blocking is not NoValue:
			_args.append(_blocking)
			if _timeout is not NoValue:
				_args.append(_timeout)
		else:
			if _timeout is not NoValue:
				_kwargs["timeout"] = _timeout
		return _args, _kwargs

	def acquire(self, *args, **kwargs):
		self._validate_args(*args, **kwargs)
		_args, _kwargs = self._merge_into_constant_args(args, kwargs)
		# Create state
		state = self._create_state(*_args, **_kwargs)
		self._enter_state(state)
		return state.acquired()
	
	def release(self):
		state = self.state
		if state is None:
			raise RuntimeError(utils.method.msg_kw("Lock is not acquired"))
		if state.acquired():
			self._locked = False
			self._owner = None
		self._exit_state(state=state)

	def acquired(self):
		state = self.state
		return state and state.acquired()
	
	def locked(self):
		return self._locked

	def owner(self):
		return self._owner

	def _validate_args(self, *args, **kwargs):
		assert not args or args[0] is not None
		blocking, timeout = self._decompose_args_default(*args, **kwargs)[:2]
		verify(blocking or timeout < 0, "Non-blocking lock cannot have a timeout")
		return blocking, timeout
	
	def _decompose_args(self, blocking=NoValue, timeout=NoValue, *args, **kwargs):
		return blocking, timeout, args, kwargs
	
	def _decompose_args_default(self, blocking=NoValue, timeout=NoValue, *args, **kwargs):
		_blocking = blocking if blocking is not NoValue else True
		_timeout = timeout if timeout is not NoValue else -1
		return _blocking, _timeout, args, kwargs
		
	def _create_state(self, *args, **kwargs):
		return ParameterizedLockState(self, *args, **kwargs)

	def _enter(self, blocking=True, timeout=-1, *args, **kwargs):
		# print(utils.method.msg_kw(f"Acquiring lock '{self._obj}'"))
		# log.verbose(utils.method.msg_kw(f"Acquiring lock '{self._obj}'"))
		acquired = self._obj.acquire(blocking, timeout, *args, **kwargs)
		if not acquired:
			if timeout >= 0:
				if self._except_on_timeout:
					if self._except_on_timeout is True:
						raise RuntimeError(f"Failed to enter '{self._obj}' within {timeout} seconds")
					raise self._except_on_timeout
			self._locked = acquired
			if acquired:
				state = self.state
				self._owner = state.owner()
		return acquired

	def _exit_by_condition(self, exc_type, exc_value, traceback):
		# print(utils.method.msg(f"Releasing lock '{self._obj}'"))
		# log.verbose(utils.method.msg(f"Releasing lock '{self._obj}'"))
		self._obj.release()
		# print(utils.method.msg(f"Released lock '{self._obj}'"))

	def __repr__(self):
		return f"{self.__class__.__name__}(lock={self._obj}, locked={self._locked}, owner={self._owner})"
	
	def set_constant_args(self, *args, **kwargs):
		self._validate_args(*args, **kwargs)
		return super().set_constant_args(*args, **kwargs)
