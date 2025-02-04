import threading

from utils.base_task_scheduler import LoopOperatorBase, TaskSchedulerBase
from utils.concurrency.thread_guard import ThreadGuard
from utils.debug import wrap_debug_lock


class ThreadTaskScheduler(ThreadGuard, TaskSchedulerBase):
	context_package = threading
	context_title = "thread"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._lock = wrap_debug_lock(threading.RLock())
		class LoopOperator(LoopOperatorBase):
			context_package = self.context_package
		self._loop_operator = LoopOperator()
		self.loop_operator.enter_lock = wrap_debug_lock(threading.RLock())
