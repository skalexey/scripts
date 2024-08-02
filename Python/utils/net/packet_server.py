import struct
from abc import ABC, abstractmethod

import utils.net.server
from utils.log.logger import Logger
from utils.memory.buffer import Buffer
from utils.net.server import log


class Packet:
	def __init__(self):
		self.size = 0
		self.data = bytearray()

	def __bool__(self):
		return bool(self.data) and len(self.data) == self.size

class PacketServer(utils.net.server.Server, ABC):
	max_buffer_size = 65535

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._buffer = (Buffer(), None)
		self._incoming_packets = {} # Buffer per address

	def _handle_client_connection(self, conn):
		log(utils.method.msg_kw(f"Connected"))
		while True:
			try:
				data = self._next_packet(conn)
				if not data:
					break
				if not self._process_packet(data):
					break
			except Exception as e:
				log(utils.method.msg_kw(f"Error handling incoming packet: '{e!r}'"))
				raise

	@abstractmethod
	def _process_packet(self, data) -> bool: # Return True to continue handling packets
		pass

	def _incoming_packet(self, addr):
		packet = self._incoming_packets.get(addr)
		if packet is None:
			packet = Packet()
			self._incoming_packets[addr] = packet
		return packet

	def _next_packet(self, conn):
		while True:
			buffer, addr = self._next_data(conn)
			if not buffer:
				return None
			packet = self._incoming_packet(addr)
			if packet.size == 0:
				raw_msglen = buffer.read(4)
				packet.size = struct.unpack('>I', raw_msglen)[0]
			packet.data.extend(buffer.read(packet.size - len(packet.data)))
			if packet:
				del self._incoming_packets[addr]
				return packet.data

	def _next_data(self, conn):
		buffer, addr = self._buffer
		if not buffer:
			data, addr = conn.recvfrom(self.max_buffer_size)
			if data is None:
				return None, None
			buffer.set_data(data)
			self._buffer = (buffer, addr)
		return buffer, addr
