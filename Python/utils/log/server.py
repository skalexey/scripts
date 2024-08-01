import os
import pickle
import threading

import utils  # Lazy import for less important modules
import utils.file
import utils.method
import utils.net.tcp.server
from utils.live import verify
from utils.log import compose_log_message, print_log
from utils.log.logger import LogLevel
from utils.net.packet_server import PacketServer
from utils.net.server import log
from utils.net.udp.server import Server as UDPServer


class LogServer(PacketServer, UDPServer):
	def __init__(self):
		super().__init__()
		self.files = {}
		self.storage_path = "logs"
		self.print_logs = True
		self.file_lock = threading.Lock()

	@property
	def print_logs(self):
		return self._log_func == print_log
	
	@print_logs.setter
	def print_logs(self, value):
		self._log_func = print_log if value else compose_log_message

	def _process_packet(self, data):
		try:
			packet = pickle.loads(data)
			self.on_log(packet)
		except Exception as e:
			log.error(utils.method.msg_kw(f"Failed to process log packet: '{e!r}'"))
			raise
		return True

	def shutdown(self):
		with self.file_lock:
			for file_info in self.files.values():
				file_info.file.close()
		super().shutdown()

	def open_file(self, level, fpath=None): # fpath - optional for overriding the default path generated for the given level
		_log_level = level or LogLevel.VERBOSE
		level_name = _log_level.name.lower()
		file_name_addition = f"-{level_name}" if level else ""
		fname = utils.log.log_fname(file_name_addition)
		_fpath = os.path.abspath(fpath or os.path.join(self.storage_path, fname))
		os.makedirs(os.path.dirname(_fpath), exist_ok=True)
		# Check if the file is already opened
		verify(not utils.file.is_open(_fpath), f"Log file '{_fpath}' is already opened for writing")
		file = open(_fpath, "a")
		file_info = self.FileInfo(file, _log_level)
		verify(_log_level not in self.files, f"Log level '{level_name}' is already set")
		self.files[_log_level] = file_info
		log(utils.method.msg_kw(f"Opened log file '{_fpath}' for level '{level_name}'"))
		return file_info

	def on_log(self, packet):
		# Parse level as the sequence of characters between '[' and ']' in the beginning of the message
		full_message = None
		for file_info in self.files.values():
			if packet.level >= file_info.level:
				if full_message is None:
					log = self._log_func(packet.message, packet.level, packet.title, packet.addition, packet.timestamp)
					full_message = log.full_message
				file = file_info.file
				with self.file_lock:
					if file.closed:
						continue
					file.write(f"{full_message}\n")
					file.flush()
		return full_message

	# Redirects logs with level move or equal than the given level into a separate file
	def open_files(self, *levels):
		for level in levels:
			self.open_file(level=level)
		return self.files
	
	class FileInfo:
		def __init__(self, file, level):
			self.file = file
			self.level = level
