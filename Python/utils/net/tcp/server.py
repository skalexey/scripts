import threading

import utils.method
import utils.net.server
import utils.net.tcp.connection
from utils.net.server import log  # Special logger for server


class Server(utils.net.server.Server):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def _create_connection(self):
		return utils.net.tcp.connection.Connection(('', self.port))

	def _on_run(self):
		super()._on_run()
		while True:
			conn, addr = self._connection.accept()
			client_thread = threading.Thread(target=self._handle_client, args=(conn, addr), name=f"TCP Server Client '{addr}'")
			client_thread.daemon = True
			client_thread.start()

	def _handle_client(self, conn, addr):
		with conn:
			log(utils.method.msg_kw(f"Client connected"))
			while self._handle_client_connection(conn):
				pass
			log(utils.method.msg_kw(f"Client disconnected"))
