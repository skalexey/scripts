import os
import threading
from datetime import datetime

from utils.log.subscriptions import g_on_log


def store_to_file(fpath, data):
	os.makedirs(fpath, exist_ok=True)
	with open(fpath, 'w') as f:
		f.write(data)

def log_fname(postfix=''):
	return f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{postfix}.log"

def store(data, prefix=''):
	store_to_file(prefix + log_fname(), data)

def redirect_to_file(fpath=None):
	_fpath = fpath or f"logs/{log_fname()}"
	os.makedirs(os.path.dirname(_fpath), exist_ok=True)
	file = open(_fpath, "a")
	lock = threading.RLock()
	class State:
		def __init__(self):
			self.writing = False
			self.queue = []

	state = State()
	def on_log(log):
		full_message, message, level, title, time = log
		with lock:
			state.queue.append(full_message)
			if not state.writing: # Flush invokes garbage collector that may cause new logs coming from destructors, but it doesn't allow recursive flush calls.
				state.writing = True
				for queued_message in state.queue:
					file.write(f"{queued_message}\n")
				state.queue.clear()
				file.flush()
				state.writing = False
				
	g_on_log.subscribe(on_log, file)
	return file