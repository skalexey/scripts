from threading import current_thread

from utils.concurrency.base_guard import (
    ContextGuard,
    allow_any_context,
    allow_any_context_with_lock,
    apply_context_check,
)


def allow_any_thread(method_func):
	return allow_any_context(method_func)

def allow_any_thread_with_lock(lock_name):
	return allow_any_context_with_lock(lock_name)

@apply_context_check
class ThreadGuard(ContextGuard):
	_context_getter = current_thread
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def allow_thread(self, thread):
		self.allow_context(thread)

	def allow_thread_name(self, thread_name):
		self.allow_context_name(thread_name)
