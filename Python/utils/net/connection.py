from abc import ABC, abstractmethod


# Supposed to be opened right away upon creation
class Connection(ABC):
	def __init__(self, address, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.address = address
		self.socket = None

	@abstractmethod
	def connect(self):
		pass

	@abstractmethod
	def listen(self):
		pass

	@abstractmethod
	def send(self, data):
		pass

	@abstractmethod
	def recvfrom(self, size) -> tuple[bytearray, str]: # Any connection must implement it for abstraction
		pass

	def recv(self, size):
		message, addr = self.recvfrom(size)
		return message

	def close(self):
		self.socket.close()

	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.socket:
			self.close()

	def __bool__(self):
		# Call __bool__ on the socket object
		if not bool(self.socket):
			return False
		if not self.socket.fileno() != -1:
			return False
		return True
