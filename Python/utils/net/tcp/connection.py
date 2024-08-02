import socket

import utils.net.connection


class Connection(utils.net.connection.Connection):
	def __init__(self, address, *args, **kwargs):
		super().__init__(address, *args, **kwargs)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if address[0]:
			self.connect()

	def connect(self):
		with self.lock:
			self.socket.connect(self.address)

	def listen(self):
		with self.lock:
			self.socket.bind(self.address)
			self.socket.listen()

	def accept(self):
		with self.lock:
			if self:
				return self.socket.accept()
			return None

	def send(self, data):
		with self.lock:
			if self:
				return self.socket.sendall(data)
		return None

	def recvfrom(self, size):
		with self.lock:
			if self:
				return self.socket.recv(size), self.address
			return None, None

	def close(self):
		with self.lock:
			if self:
				return self.socket.close()
			return None
