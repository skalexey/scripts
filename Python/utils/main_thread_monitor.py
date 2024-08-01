import threading
from time import sleep

import utils.subscriptions


class MainThreadMonitor:
	def __init__(self):
		self.thread = threading.Thread(target=self._job)

	def _job(self):
		main_thread = threading.main_thread()
		while main_thread.is_alive():
			sleep(0.1)
		utils.subscriptions.on_exit.set_result(True)
