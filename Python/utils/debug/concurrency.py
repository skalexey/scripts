import threading
from abc import ABC, abstractmethod

from utils.log.logger import Logger

log = Logger()

class ThreadInfo:
	def __init__(self, thread):
		self.thread = thread
		self.id = thread.ident
		self.name = thread.name
		super().__init__()

	def __str__(self):
		return f"ThreadInfo(id={self.id}, name={self.name})"

	def __repr__(self):
		return self.__str__()

	def __eq__(self, other):
		return self.id == other.id

	def __hash__(self):
		return hash(self.id)

class ConcurrentEntity(ABC):
	def __init__(self):
		self._sytem_lock = threading.RLock()
		self._system_lock_timeout = 100
		self._threads = {}
		super().__init__()

	@abstractmethod
	def acquire_impl(self, *args, **kwargs):
		# Return True if the lock has been acquired
		pass

	@abstractmethod
	def release_impl(self):
		# Return True if the lock is now available for acquisition by other threads
		pass

	def acquire(self, *args, **kwargs):
		# Print args and kwargs
		args_str = ", ".join([str(arg) for arg in args])
		kwargs_str = ", ".join([f"{key}={value}" for key, value in kwargs.items()])
		info_str = f"{args_str}, {kwargs_str}" if args_str else kwargs_str
		log.debug(f"{self} (CuncurrentEntity): acquire({info_str})")
		# if self._sytem_lock.acquire(timeout=self._system_lock_timeout):
		result = self.acquire_impl(*args, **kwargs)
		# self._sytem_lock.release()
		if result:
			log.debug(f"{self} (CuncurrentEntity): acquire(): acquire_impl() -> True")
		else:
			log.warning(f"{self} (CuncurrentEntity): acquire(): Could not acquire the lock")
		return result
		# else:
		# 	raise RuntimeError(f"{self} (ConcurrentEntity): acquire(): Could not acquire the system lock")

	def release(self):
		log.debug(f"{self} (CuncurrentEntity): release(): before")
		if not self.is_locked:
			raise RuntimeError("Release called on an unlocked lock")
		# if self._sytem_lock.acquire(timeout=self._system_lock_timeout):
		result = self.release_impl()
		# self._sytem_lock.release()
		if result:
			log.debug(f"{self} (CuncurrentEntity): release(): release_impl() -> True")
		else:
			log.debug(f"{self} (CuncurrentEntity): release(): still acquired")
		return result
		# else:
		# 	raise RuntimeError(f"{self} (ConcurrentEntity): release(): Could not acquire the system lock")

	def create_thread_info(self, thread):
		return ThreadInfo(thread)

	@property
	def owner_id(self):
		owner = self.owner
		return owner.ident if owner is not None else None

	@property
	@abstractmethod
	def owner(self):
		pass

	@property
	def owner_name(self):
		owner = self.owner
		return owner.name if owner is not None else None

	@property
	def caller(self):
		return threading.current_thread()

	@property
	def caller_name(self):
		thread = self.caller
		return thread.name if thread.name is not None else thread.ident

	@property
	def caller_id(self):
		return self.caller.ident

	@property
	def caller_info(self):
		thread_info = self.get_caller_info()
		if thread_info is None:
			if self._sytem_lock.acquire(timeout=self._system_lock_timeout):
				thread_info = self.create_thread_info(self.caller)
				self._threads[self.caller_id] = thread_info
				self._sytem_lock.release()
			else:
				raise RuntimeError("Could not acquire the system lock")
		return thread_info

	def get_caller_info(self):
		return self.get_thread_info(self.caller_id)

	def get_thread_info(self, thread_id):
		if self._sytem_lock.acquire(timeout=self._system_lock_timeout):
			result = self._threads.get(thread_id)
			self._sytem_lock.release()
			return result
		else:
			raise RuntimeError("Could not acquire the system lock")

	def _data_str_(self):
		return f"owner: {self.owner_name}"

	def __str__(self):
		return f" [{self.caller_name}] {self.__class__.__name__} ({self._data_str_()})"

class SingleThreadOwnershipEntity(ConcurrentEntity):
	@ConcurrentEntity.owner.getter
	def owner(self):
		if len(self._threads) == 0:
			return None
		values = list(self._threads.values())
		return values[0]

	def is_locked(self):
		return self.owner is not None

	def acquire_impl(self, *args, **kwargs):
		log.verbose(f"{self}	(SingleThreadOwnershipEntity): acquire_impl()")
		# Register thread info for this thread if not exists as an owner indicator
		self.caller_info
		log.verbose(f"{self}	(SingleThreadOwnershipEntity): acquire_impl done")
		return True

	def release_impl(self):
		log.verbose(f"{self}	(SingleThreadOwnershipEntity): release_impl()")
		# Unregister thread info for this thread if exists indicating there is no owner anymore
		del self._threads[self.caller_id]
		log.verbose(f"{self}	(SingleThreadOwnershipEntity): release_impl done")
		return True

class DebugAbstractLock(SingleThreadOwnershipEntity, ABC):
	def __init__(self):
		super().__init__()
		self._acquire_release_lock = threading.RLock()
		self._acquire_release_lock_timeout = 100

	@property
	@abstractmethod
	def lock(self):
		pass

	def acquire_impl(self, *args, **kwargs):
		if not self._acquire_release_lock.acquire(timeout=self._acquire_release_lock_timeout):
			raise RuntimeError(f"{self}		(DebugAbstractLock): acquire_impl(): Could not acquire the acquire-release lock (2)")
		log.debug(f"{self}		(DebugAbstractLock): acquire_impl()")
		if self.lock.acquire(*args, **kwargs):
			log.info(f"{self}		(DebugAbstractLock): acquired")
			return super().acquire_impl(*args, **kwargs)
		return False

	def release_impl(self):
		log.debug(f"{self}		(DebugAbstractLock): release_impl()")
		self.lock.release()
		if self.is_locked():
			log.info(f"{self}		(DebugAbstractLock): still acquired")
			return False
		super().release_impl()
		log.info(f"{self}		(DebugAbstractLock): released")
		self._acquire_release_lock.release()
		return True

	def __enter__(self):
		self.acquire()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.release()

class DebugLock(DebugAbstractLock):
	def __init__(self):
		super().__init__()
		self._lock = threading.Lock()

	@DebugAbstractLock.lock.getter
	def lock(self):
		return self._lock

	def is_locked(self):
		low_check = self._lock.locked()
		# high_check = super().is_locked()
		# assert(low_check == high_check)
		return low_check

class RLockThreadInfo(ThreadInfo):
	def __init__(self, thread):
		super().__init__(thread)
		self.recursive_calls = 0

	def __str__(self):
		return f"RLockThreadInfo(id={self.id}, name={self.name}, recursive_calls={self.recursive_calls})"

	def __repr__(self):
		return self.__str__()

class DebugRLock(DebugAbstractLock):
	def __init__(self):
		super().__init__()
		self._lock = threading.RLock()

	@DebugAbstractLock.lock.getter
	def lock(self):
		return self._lock

	# Override
	def is_locked(self):
		low_check = self._lock._is_owned()
		# high_check = super().is_locked()
		this_check = self.recursive_calls > 0
		# assert(low_check == high_check)
		assert(low_check == this_check)
		return this_check

	# Override
	def create_thread_info(self, thread):
		return RLockThreadInfo(thread)

	@property
	def recursive_calls(self):
		caller_info = self.get_caller_info()
		result = caller_info.recursive_calls if caller_info is not None else 0
		return result

	@recursive_calls.setter
	def recursive_calls(self, value):
		self.caller_info.recursive_calls = value

	def acquire_impl(self, *args, **kwargs):
		log.debug(f"{self}			acquire_impl()")
		if super().acquire_impl(*args, **kwargs):
			self.recursive_calls += 1
			log.debug(f"{self}			acquire_impl(): after recursive_calls += 1")
			return True
		return False

	def release_impl(self):
		log.debug(f"{self}			release_impl()")
		if self.recursive_calls == 0:
			raise RuntimeError("Calling release_impl() on a not owned lock")
		self.recursive_calls -= 1
		log.debug(f"{self}			release_impl(): after recursive_calls -= 1")
		return super().release_impl()

	def _data_str_(self):
		data_str = super()._data_str_()
		return f"{data_str}, recursive_calls={self.recursive_calls}"
