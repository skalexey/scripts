
# Does not raise CancelledError
def wait_all_tasks(self):
	tasks = []
	for task_info in list(self._tasks.values()):
		tasks.append(task_info.task)
	async def wait_tasks():
		await asyncio.wait(tasks)
	self.loop.run_until_complete(wait_tasks())

# Does not raise CancelledError (return_exceptions=True)
def wait_all_tasks(self):
	tasks = []
	for task_info in list(self._tasks.values()):
		tasks.append(task_info.task)
	async def wait_tasks():
		await asyncio.gather(*tasks, return_exceptions=True)
	self.loop.run_until_complete(wait_tasks())

# Raises CancelledError (no return_exceptions)
def wait_all_tasks(self):
	tasks = []
	for task_info in list(self._tasks.values()):
		tasks.append(task_info.task)
	async def wait_tasks():
		await asyncio.gather(*tasks)
	self.loop.run_until_complete(wait_tasks())

# Raises CancelledError
def wait_all_tasks(self):
	tasks = []
	for task_info in list(self._tasks.values()):
		tasks.append(task_info.task)
	assert len(tasks) == 1
	self.loop.run_until_complete(tasks[0])

# Raises CancelledError
def wait_all_tasks(self):
	for task_info in list(self._tasks.values()):
		try:
			task_info.future.get_loop().run_until_complete(task_info.task)
		except asyncio.CancelledError:
			log.info(f"Task has been cancelled (tas_info: {task_info})")

# Raises CancelledError
def wait_all_tasks(self):
	for task_info in list(self._tasks.values()):
		try:
			task_info.future.get_loop().run_until_complete(task_info.future)
		except asyncio.CancelledError:
			log.info(f"Task has been cancelled (tas_info: {task_info})")



# V1
class LoopOperatorEnter:
	def __init__(self, loop=None, try_use=None, check_if_free=None, operator=None):
		self.loop = loop
		self.try_use = try_use
		self.check_if_free= check_if_free
		self._try_result = None
		self._check_result = None
		self.operator = operator

	def try_result(self):
		return self._try_result

	def __getattr__(self, name):
		return getattr(self.operator, name)

	def __enter__(self):
		with self.operator.enter_lock:
			log.debug(utils.method.msg_kw(f"Thread '{threading.current_thread().name}' is entering the loop operator"))
			if self.operator.is_operating():
				msg = utils.method.msg_kw(f"Loop is already operating by '{self.operator.thread_id}'")
				if self.try_use:
					log.debug(msg)
					self._try_result = False
					return self
				raise RuntimeError(msg)
			if self.loop.is_running():
				raise RuntimeError("Unknown operator is already running the loop")
			if self.try_use:
				self._try_result = True
			self.operator.thread_id = threading.current_thread().name
			log.debug(utils.method.msg_kw(f"Thread '{self.operator.thread_id}' entered the loop operator"))
			return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		operator_thread_id = self.operator.thread_id
		is_owner = operator_thread_id == threading.current_thread().name
		msg_addition = "" if is_owner else " (not the owner)"
		log.debug(utils.method.msg_kw(f"Thread '{operator_thread_id}'{msg_addition} is exiting the loop operator"))
		if is_owner:
			self.operator.thread_id = None
		log.debug(utils.method.msg_kw(f"Thread '{operator_thread_id}'{msg_addition} exited the loop operator"))

def __call__(self, loop):
	params = self.LoopOperatorEnter(loop=loop, operator=self)
	return params

def try_use(self, loop):
	params = self.LoopOperatorEnter(loop=loop, try_use=True, operator=self)
	return params

def check_if_free(self, loop):
	params = self.LoopOperatorEnter(loop=loop, check_if_free=True, operator=self)
	return params