import utils  # Lazy import for less important modules
from utils.concurrency.parameterized_lock import ParameterizedLock
from utils.context import GlobalContext
from utils.log.logger import Logger

log = Logger()

def is_debug():
	attr = getattr(GlobalContext, "is_live", None)
	return (attr or False) is False

def wrap_debug_lock(lock, blocking=True, timeout=None, *args, **kwargs):
	if is_debug():
		_lock = ParameterizedLock(lock, except_on_timeout=True)
		_timeout = timeout if timeout is not None else 30
		_lock.set_constant_args(blocking, _timeout, *args, **kwargs)
	else:
		_lock = lock
	return _lock

def object_by_address(address):
	import ctypes
	return ctypes.cast(address, ctypes.py_object).value

def inspect_address(address):
	obj = object_by_address(address)
	attrs = dir(obj)
	_vars = vars(obj)
	log.debug(f"Address: {address}\nObject: {obj}\nAttributes:\n{attrs}\nVars:\n{_vars}\n\n")


class RecursionInfo:
	def __init__(self, level=0, max_level=0, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.level = level
		self.max_level = max_level
		self.ref_ids = utils.collection.ordered_set.OrderedSet()

	def __str__(self):
		return f"Recursion level: {self.level}"

	def __repr__(self):
		return self.__str__()


class ReferrersRecursionInfo(RecursionInfo):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.indent_addition = utils.log.IndentAddition()


def inspect_referrers(self, obj, recursion=None):
	import gc

	from utils.collection.weak_list import WeakList
	from utils.log import IndentAddition
	from utils.memory import deref_if_weak_proxy, wrap_weakable
	recursion_info = recursion if isinstance(recursion, RecursionInfo) else (ReferrersRecursionInfo() if recursion is True else None)
	indent_addition = recursion_info.indent_addition if recursion_info is not None else IndentAddition()
	if recursion_info is not None:
		if id(obj) in recursion_info.ref_ids:
			log.debug(f"Cyclic reference detected: '{obj}'. Stop recursion.", addition=indent_addition)
			return
		recursion_info.ref_ids.add(id(obj))
	refs = WeakList(gc.get_referrers(obj))
	filtered_refs = []
	for ref in refs:
		if ref == obj:
			continue
		filtered_refs.append(ref)
	refs = filtered_refs
	del filtered_refs
	log.debug(f"Object memid={id(obj)}: {obj} referrers({len(refs)}):", addition=indent_addition)
	ib = indent_addition.indent_block()
	for i in range(len(refs)):
		ref = refs[i]
		ref_id = id(ref)
		log.debug(f"Referrer ID: {ref_id}, Type: '{type(ref)}': {ref}", addition=indent_addition)
		if isinstance(ref, dict):
			for key, value in ref.items():
				if value is obj:
					log.debug(f"Found in dict key: '{key}'", addition=indent_addition)
			del key, value
		elif isinstance(ref, list):
			for index, item in enumerate(ref):
				if item is obj:
					log.debug(f"Found in list index: '{index}'", addition=indent_addition)
			del index, item
	if recursion_info is not None:
		# recursion_level = recursion if isinstance(recursion, int) else 0
		if recursion_info.level < recursion_info.max_level:
			recursion_info.level += 1
			for i in range(len(refs)):
				inspect_referrers(self, deref_if_weak_proxy(ref), recursion_info)
