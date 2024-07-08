
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

