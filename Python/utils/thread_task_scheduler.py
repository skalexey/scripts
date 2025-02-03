import threading

from utils.base_task_scheduler import TaskSchedulerBase
from utils.concurrency.thread_guard import ThreadGuard


class ThreadTaskScheduler(ThreadGuard, TaskSchedulerBase):
	context_package = threading
	context_title = "thread"
