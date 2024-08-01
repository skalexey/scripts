import os
import pickle
import struct
import threading
import weakref
from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum
from time import time

# All utils imports in logger must be lazy to avoid circular imports since logger is imported in many modules
import utils  # Lazy import for less important modules

log_lock = threading.Lock()
g_addition = None

class LogLevel(IntEnum):
	VERBOSE = 0
	LOOP_VERBOSE = 1 # Loop iterations that spam significantly
	LOOP = 2 # Loop iterations
	DEBUG = 3
	INFO = 4
	SUCCESS = 5
	ATTENTION = 6
	WARNING = 7
	ERROR = 8
	CRITICAL = 9
	PRINT = 10

	def sign(level):
		level_str = level.name
		# Find the first letter of each part separated by _
		split = level_str.split("_")
		return "".join([s[0] for s in split])
	
	@classmethod
	def _gen_sign_map(cls):
		sign_map = {}
		for level in cls:
			sign_map[cls.sign(level)] = level
		cls._sign_map = sign_map
	
	@classmethod
	def from_sign(cls, sign):
		return cls._sign_map.get(sign)

	@classmethod
	def items(cls):
		return cls.__members__.items()

	@classmethod
	def values(cls):
		return cls.__members__.values()

	@classmethod
	def keys(cls):
		return cls.__members__.keys()
	
LogLevel._gen_sign_map()


class LogPacket:
	def __init__(self, timestamp, message, level, title=None, addition=None):
		assert isinstance(level, LogLevel)
		self.timestamp = timestamp
		self.message = message
		self.level = level
		self.title = title
		self.addition = addition

class Log:
	def __init__(self, message, level, title=None, addition=None, timestamp=None):
		self.packet = LogPacket(timestamp, message, level, title, addition)
		self._full_message = None
		self._datetime = None

	def extract(self):
		return self.full_message, self.message, self.level, self.title, self.addition, self.datetime

	@property
	def full_message(self):
		if self._full_message is None:
			self._compose_log_message()
		return self._full_message
	
	@property
	def datetime(self):
		if self._datetime is None:
			self._compose_log_message()
		return self._datetime
	
	def _compose_log_message(self):
		self._full_message, self._datetime = compose_log_message(self.message, self.level, self.title, self.addition, self.timestamp)

	def __getattr__(self, name):
		return getattr(self.packet, name)


def compose_log_message(message, level=LogLevel.PRINT, log_title=None, log_addition=None, timestamp=None):
	_timestamp = timestamp or time()
	now = datetime.fromtimestamp(_timestamp)
	try:
		_datetime = now.strftime("%H:%M:%S.%f")
	except ImportError:
		_datetime = "no time"
	level_sign = LogLevel.sign(level)
	level_prefix = f"[{level_sign}] " if level_sign else "    "
	log_addition_str = str(g_addition or "") + str(log_addition or "")
	msg = f"{level_prefix}[{_datetime}] {log_addition_str}{message}"
	return msg, _datetime

# Variadic arguments
def print_log(message, level=LogLevel.PRINT, log_title=None, log_addition=None, timestamp=None):
	# Print the log level,time (hour, minute, second, and microsecond), and the message
	log = Log(message, level, log_title, log_addition, timestamp)
	with log_lock:
		print(log.full_message)
	return log

# Allow to override global log function without affecting imports in other modules
def log(*args, **kwargs):
	return _log_impl(*args, **kwargs)

# log function is connected to the print_log by default, but can be redirected to a file or a server
_log_impl = print_log

# Generate log_<level_name> functions
def _gen_log_funcs(base_log_func):
	funcs = {}

	def gen_log_fn(level_name, level_value):
		def log_level(*args, **kwargs):
			result = base_log_func(*args, **kwargs, level=level_value)
			# result: (msg, message, level, self.log_title, current_time)
			return result
		return log_level
	
	for key, value in LogLevel.items():
		name = key.lower()
		funcs[name] = gen_log_fn(name, value)

	return funcs

def _init():
	funcs = _gen_log_funcs(log)
	for level_name, func in funcs.items():
		globals()[f"log_{level_name}"] = func

_init()

def log_to_server(connection, message, level=LogLevel.PRINT, log_title=None, log_addition=None):
	if connection:
		# Pack all the data into a packet <packet size:4bytes><packet data>
		timestamp = time()
		log = Log(message, level, log_title, log_addition, timestamp)
		try:
			packet_data = pickle.dumps(log.packet)
			data = struct.pack('>I', len(packet_data)) + packet_data
			connection.send(data)
			# connection.sendto(message, server_address)
		except Exception as e:
			print(f"Failed to send log to server: '{e!r}'. Log message: {log.full_message}")
			if not isinstance(e, ImportError):
				raise
		return log
	else:
		raise ValueError(utils.function.msg_kw("Connection is invalid"))
	

def redirect_to_file(fpath=None, level=None, subscription=None, *args, **kwargs):
	_log_level = level or LogLevel.VERBOSE
	_fpath = fpath or f"logs/{log_fname(*args, **kwargs)}"
	os.makedirs(os.path.dirname(_fpath), exist_ok=True)
	# Check if the file is already opened
	utils.live.verify(not utils.file.is_open(_fpath), f"Log file '{_fpath}' is already opened for writing")
	file = open(_fpath, "a")
	lock = threading.RLock()
	class State:
		def __init__(self):
			self.writing = False
			self.queue = []

	state = State()
	def on_log(log):
		full_message, message, level, title, addition, time = log.extract()
		if level < _log_level:
			return
		with lock:
			state.queue.append(full_message)
			if not state.writing: # Flush invokes garbage collector that may cause new logs coming from destructors, but it doesn't allow recursive flush calls.
				state.writing = True
				for queued_message in state.queue:
					file.write(f"{queued_message}\n")
				state.queue.clear()
				file.flush()
				state.writing = False
	_subscription = subscription or utils.log.subscriptions.g_on_log
	_subscription.subscribe(on_log, file)
	return file


def redirect_to_file_levels(*levels):
	files = []
	for level in levels:
		file = redirect_to_file(level=level, postfix=f"-{level.name.lower()}")
		files.append(file)
	return files

g_server = None
g_connection = None

def gen_redirect_to_server_func(address):
	from utils.concurrency.thread_local_proxy import ThreadLocalProxy
	from utils.net.udp.connection import Connection as UDPConnection
	ip, port = address.split(':')
	port = int(port)
	# _connection = socket.create_connection((ip, port))
	_connection = ThreadLocalProxy(UDPConnection, (ip, port))

	def log_override_to_server(*args, **kwargs):
		return log_to_server(g_connection, *args, **kwargs)

	return log_override_to_server, _connection

def redirect_to_server(address):
	# Override the global log function
	global _log_impl, g_connection
	utils.live.verify(g_connection is None, "Connection already established")
	_log_impl, g_connection = gen_redirect_to_server_func(address)
	return g_connection

def start_server(port, *levels, server=None):
	if server is None:
		global g_server
		utils.live.verify(g_server is None, "Server already started")
		from utils.log.server import LogServer
		_server = LogServer()
		g_server = _server
	else:
		_server = server
	_levels = levels or [LogLevel.VERBOSE]
	_server.open_files(*_levels)
	_server.start(port)
	return _server


class IndentBlock:
	def __init__(self, logger):
		logger.indent += 1

		def finalize(logger=logger):
			logger.indent -= 1

		self.finalizer = weakref.finalize(self, finalize)


class LogAddition(ABC):
	@abstractmethod
	def __str__(self):
		pass

	def __add__(self, other):
		if isinstance(other, str):
			return str(self) + other
		return str(self) + str(other)

	def __radd__(self, other):
		if isinstance(other, str):
			return other + str(self)
		return str(other) + str(self)


class IndentAddition(LogAddition):
	def __init__(self):
		self.indent = 0

	def indent_block(self):
		return IndentBlock(self)

	def __str__(self):
		return "  " * self.indent


class CombinedAddition(LogAddition):
	def __init__(self, *additions):
		self.additions = []
		for addition in additions:
			if addition:
				self.additions.append(addition)

	def __str__(self):
		return "".join([str(a) for a in self.additions])


class TitleAddition(LogAddition):
	def __init__(self, title):
		if not title:
			raise ValueError(utils.method.msg("Title must not be empty"))
		self.title = title

	def __str__(self):
		return f"[{self.title}]: "


def store_to_file(fpath, data):
	os.makedirs(fpath, exist_ok=True)
	with open(fpath, 'w') as f:
		f.write(data)

def log_fname(postfix=''):
	return f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{postfix}.log"

def store(data, prefix=''):
	store_to_file(prefix + log_fname(), data)

def set_global_addition(addition):
	g_addition = addition
