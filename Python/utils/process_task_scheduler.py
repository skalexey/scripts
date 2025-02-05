import multiprocessing

from utils.base_task_scheduler import LoopOperatorBase, TaskSchedulerBase
from utils.concurrency.process_guard import ProcessGuard
from utils.multiprocessing.intrstate import MultiprocessIntrstate


class LoopOperator(LoopOperatorBase):
	context_package = multiprocessing

class ProcessTaskScheduler(ProcessGuard, TaskSchedulerBase, MultiprocessIntrstate):
	context_package = multiprocessing
	context_title = "process"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__dict__["_queue"] = None
		self.on_update = None
		excluded = []
		success = False
		tmp = self.__dict__
		self.__dict__ = multiprocessing.Manager().dict()
		self.__dict__.update(tmp)
		self._loop_operator = LoopOperator()
		self.loop_operator.enter_lock = multiprocessing.RLock()
		self._lock = multiprocessing.RLock()
