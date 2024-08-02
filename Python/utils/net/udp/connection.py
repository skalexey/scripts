import socket

import utils.method
import utils.net.connection


class Connection(utils.net.connection.Connection):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def connect(self):
		raise NotImplementedError(utils.method.msg_kw("UDP does not support connecting. Use send() right away."))

	def listen(self):
		with self.lock:
			return self.socket.bind(self.address)

	def accept(self):
		raise NotImplementedError(utils.method.msg_kw("UDP does not support accepting"))

	def send(self, data):
		with self.lock:
			if self:
				try:
					self.socket.sendto(data, self.address)
				except Exception as e:
					print(f"Error sending data: '{e}'")
			return None

	def recvfrom(self, size):
		with self.lock:
			if self:
				return self.socket.recvfrom(size)
			return None, None
