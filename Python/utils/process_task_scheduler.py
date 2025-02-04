import multiprocessing

from utils.base_task_scheduler import LoopOperatorBase, TaskSchedulerBase
from utils.concurrency.process_guard import ProcessGuard


class ProcessTaskScheduler(ProcessGuard, TaskSchedulerBase):
	context_package = multiprocessing
	context_title = "process"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__dict__ = multiprocessing.Manager().dict(self.__dict__)
		class LoopOperator(LoopOperatorBase):
			context_package = self.context_package
		self._loop_operator = LoopOperator()
		self.loop_operator.enter_lock = multiprocessing.RLock()
		self._lock = multiprocessing.RLock()
