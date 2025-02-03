import multiprocessing

from utils.base_task_scheduler import TaskSchedulerBase
from utils.concurrency.process_guard import ProcessGuard


class ProcessTaskScheduler(ProcessGuard, TaskSchedulerBase):
	context_package = multiprocessing
	context_title = "process"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__dict__ = multiprocessing.Manager().dict(self.__dict__)
