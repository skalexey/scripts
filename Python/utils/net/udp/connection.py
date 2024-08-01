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
		self.socket.bind(self.address)

	def accept(self):
		raise NotImplementedError(utils.method.msg_kw("UDP does not support accepting"))

	def send(self, data):
		try:
			self.socket.sendto(data, self.address)
		except Exception as e:
			print(f"Error sending data: '{e}'")

	def recvfrom(self, size):
		return self.socket.recvfrom(size)
