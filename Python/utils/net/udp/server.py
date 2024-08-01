import utils.method
import utils.net.server
import utils.net.udp.connection


class Server(utils.net.server.Server):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def _create_connection(self):
		return utils.net.udp.connection.Connection(('', self.port))
	
	def _on_run(self):
		super()._on_run()
		while self._handle_client_connection(self._connection):
			pass
