import os
import threading
from abc import ABC, abstractmethod

import utils  # Lazy import
import utils.method
import utils.subscriptions
from utils.live import verify
from utils.log.logger import Logger

log = Logger()
log.redirect_to_file(postfix="-server")

class Server(ABC):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.port = None
		self._connection = None

	def start(self, port):
		self.port = port
		verify(self._connection is None, "Server is already started")
		server_thread = threading.Thread(target=self._run_server, name="LogServer")
		server_thread.daemon = True
		server_thread.start()
		utils.subscriptions.on_exit.subscribe(self.shutdown)

	@abstractmethod
	def _create_connection(self) -> object:
		pass

	def _on_run(self):
		self._connection.listen()
		log(utils.method.msg_kw(f"Server is listening on port '{self.port}'"))

	@abstractmethod
	def _handle_client_connection(self, conn, *args, **kwargs) -> bool: # False to break
		pass

	def _run_server(self):
		self._connection = self._create_connection()
		self._on_run()

	def shutdown(self):
		log(utils.method.msg_kw())
		if self._connection:
			self._connection.close()
			self._connection = None
