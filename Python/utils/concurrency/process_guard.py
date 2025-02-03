from multiprocessing import current_process

from utils.concurrency.base_guard import (
    ContextGuard,
    allow_any_context,
    allow_any_context_with_lock,
    apply_context_check,
)


def allow_any_process(method_func):
	return allow_any_context(method_func)

def allow_any_process_with_lock(lock_name):
	return allow_any_context_with_lock(lock_name)


@apply_context_check
class ProcessGuard(ContextGuard):
	_context_getter = current_process

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def allow_process(self, process):
		self.allow_context(process)

	def allow_process_name(self, process_name):
		self.allow_context_name(process_name)
