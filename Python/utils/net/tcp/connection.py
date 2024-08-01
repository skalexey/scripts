import socket

import utils.net.connection


class Connection(utils.net.connection.Connection):
	def __init__(self, address, *args, **kwargs):
		super().__init__(address, *args, **kwargs)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if address[0]:
			self.connect()

	def connect(self):
		self.socket.connect(self.address)

	def listen(self):
		self.socket.bind(self.address)
		self.socket.listen()

	def accept(self):
		return self.socket.accept()

	def send(self, data):
		self.socket.sendall(data)

	def recvfrom(self, size):
		return self.socket.recv(size), self.address

	def close(self):
		self.socket.close()
