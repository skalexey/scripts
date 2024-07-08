import asyncio
import gc
from test import *

import utils.asyncio_utils as asyncio_utils
import utils.method
from trade.strategy import Strategy
from trade.trade_context import TradeContext
from utils.log.logger import Logger
from utils.memory import SmartCallable
from utils.profile.refmanager import RefManager
from utils.profile.trackable_resource import TrackableResource
from utils.task_scheduler import TaskScheduler

log = Logger()
_globals = globals()

class E(TrackableResource):
	def __init__(self):
		super().__init__()

class D(TrackableResource):
	def __init__(self, c):
		super().__init__()
		log(utils.method.msg_v())

class C(TrackableResource):
	def __init__(self):
		super().__init__()
		d = D(self)

class B(TrackableResource):
	def __init__(self, a):
		super().__init__()
		log(utils.method.msg_v())
		self.a = a

class A(TrackableResource):
	def __init__(self):
		super().__init__()
		self.b = B(self)

def no_collect_cyclic_test():
	log(title("no_collect_cyclic_test"))
	a = A()
	a = None
	log(title("no_collect_cyclic_test end"))

def collect_cyclic_test():
	log(title("collect_cyclic_test"))
	a = A()
	log("a = None")
	a = None
	log("gc.collect()")
	gc.collect()
	log(title("collect_cyclic_test end"))

def no_collect_no_cyclic_test():
	log(title("no_collect_no_cyclic_test"))
	c = C()
	c = None
	log(title("no_collect_no_cyclic_test end"))

def dictionaries_test():
	log(title("Dictionaries Test"))
	e = E()
	d = {}
	d["e"] = e
	e.d = d
	b = B(e)
	log(title("End of Dictionaries Test"))

def circular_ref_test():
	log(title("Circular Reference Test"))
	# Don't use log.expr since it exposes objects to another stack frame and undermines the outcome of this test

	def test1():
		log(title("Test 1"))
		e = E()
		a = A()

		man = RefManager()

		def inner_scope():
			log(title("Inner Scope"))
			class F(E):
				def create_closure(self):
					def f():
						log(utils.method.msg_v(f"capturing self: {self}"))
					return f

				def capture_self(self):
					return self.create_closure()

				def __init__(self):
					super().__init__()
					log(utils.method.msg_v())
					self.capture_self()

			class G(F):
				def capture_self(self):
					self.f = super().capture_self()
					return self.f

			class H(F):
				def create_closure(self):
					l = lambda: log(utils.method.msg_v(f"capturing self: {self}"))
					return l

			class I(H, G):
				pass

			man.f = F()
			man.g = G()
			man.h = H()
			man.i = I()
			log(title("End of Inner Scope"))

		inner_scope()
		assert man.f is None, "F should have been collected since the function that has a reference to self captured in a closure has been collected"
		assert man.g is not None, "G should have not been collected since it has a reference to itself captured in a closure"
		assert man.h is None, "H should have been collected since the lambda that has a reference to self captured in a closure has been collected"
		assert man.i is not None, "I should have not been collected since it has a reference to itself captured in a lambda"
		log(title("End of Test1"))

	def asyncio_test():
		log(title("Asyncio Test"))

		man = RefManager()

		def inner_scope():
			log(title("Inner Scope"))
			class AsyncioTask(TrackableResource):
				def __init__(self):
					super().__init__()
					loop = asyncio_utils.get_event_loop()
					# self.sc = SmartCallable(self.af)
					# self.task = loop.create_task(self.sc())
					self.task = loop.create_task(self.af())

				async def af(self):
					log(utils.method.msg_kw())

				def cancel_task(self):
					log(utils.method.msg_kw("Cancelling task"))
					async def _cancel():
						# self.task.cancel()
						# await asyncio.gather(self.task, return_exceptions=True)
						# self.task = None
						pass
					loop = asyncio_utils.get_event_loop()
					loop.run_until_complete(_cancel())
					log(utils.method.msg_kw("Task has been cancelled"))

			class TaskSchedulerOwner(TrackableResource):
				def __init__(self):
					super().__init__()
					self.scheduler = TaskScheduler()
					self.scheduler.schedule_task(self.saf)

				async def saf(self):
					try:
						log(utils.method.msg_kw())
					except asyncio.CancelledError as e:
						log(utils.method.msg_v(f"Cancelled error: {e}"))
						raise e

			man.asyncio_task = AsyncioTask()
			man.task_scheduler_owner = TaskSchedulerOwner()

			log(title("End of Inner Scope"))

		inner_scope()
		
		assert man.asyncio_task is not None, "AsyncioTask should have not been collected since it has a reference to itself captured in the task object"
		assert man.task_scheduler_owner is not None, "TaskSchedulerOwner should have not been collected since it has a reference to itself captured in the task object"
		man.asyncio_task.cancel_task()
		assert man.asyncio_task is None, "AsyncioTask should have been collected since the task has been cancelled"
		log(title("End of Asyncio Test"))

	def task_scheduler_test():
		log(title("TaskScheduler Test"))

		man = RefManager()

		def inner_scope():
			log(title("Inner Scope"))

			class TaskSchedulerOwner(TrackableResource):
				def __init__(self):
					super().__init__()
					self.scheduler = TaskScheduler()
					self.scheduler.schedule_task(self.saf)

				async def saf(self):
					log(utils.method.msg_kw("Perform step 1"))
					log(utils.method.msg_kw("Perform step 2"))
					log(utils.method.msg_kw("Perform step 3"))
					log(utils.method.msg_kw("Perform step 4"))
					log(utils.method.msg_kw("Perform step 5"))
					log(utils.method.msg_kw("Perform step 6"))

			man.task_scheduler_owner = TaskSchedulerOwner()
			log(title("End of Inner Scope"))

		inner_scope()
		
		assert man.task_scheduler_owner is not None, "TaskSchedulerOwner should have not been collected since it has a reference to itself captured in the task object"
		man.task_scheduler_owner.scheduler.cancel_all_tasks()
		assert man.task_scheduler_owner is None, "TaskSchedulerOwner should have been collected since the task has been cancelled"
		log(title("End of TaskScheduler Test"))


	def strategy_test():
		log(title("Strategy Test"))
		man = RefManager()

		def inner_scope():
			log(title("Inner Scope"))
			class TestStrategy(Strategy):
				def __init__(self, context, *args, **kwargs): # context is TradeContext
					super().__init__(context=context, *args, **kwargs) # name should be passed through GeneralStrategy
					self.scheduler = utils.task_scheduler.TaskScheduler()
					self.scheduler.schedule_task(self.empty_task, 1)
				
				async def empty_task(self):
					log.debug(utils.method.msg("Empty task step 1"))
					log.debug(utils.method.msg("Empty task step 2"))
					log.debug(utils.method.msg("Empty task step 3"))
					log.debug(utils.method.msg("Empty task step 4"))
					log.debug(utils.method.msg("Empty task step 5"))
					log.debug(utils.method.msg("Empty task step 6"))

			context = TradeContext()
			man.strat = TestStrategy(context)
		
			log(title("End of Inner Scope"))

		

		inner_scope()
		assert man.strat is not None, "Strategy should have not been collected since it has a reference to itself captured in the task object"
		man.strat.join()
		assert man.strat is None, "Strategy should have been collected since the task has been cancelled"

		log(title("End of Strategy Test"))

	test1()
	asyncio_test()
	task_scheduler_test()
	strategy_test()
	log(title("End of Circular Reference Test"))
	

def test():
	log(title("Test"))
	# no_collect_cyclic_test()
	# collect_cyclic_test()
	# no_collect_no_cyclic_test()
	# dictionaries_test()
	circular_ref_test()
	log(title("End of Test"))

run()

