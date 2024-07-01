import os
from pathlib import Path

import utils.method
from utils.log.logger import Logger

log = Logger()

class Session:
	# Session creates a directory in root_path named with the id for all the data.
	def __init__(self, id, root_path):
		log.info(utils.method.msg_kw(f"Creating a session"))
		self.id = id
		self.root_path = os.path.normpath(root_path)
		self.storage_path = os.path.join(self.root_path, id)
		if os.path.exists(self.storage_path):
			log.info(utils.method.msg_kw(f"Already exists. It will use the existing resources."))
		else:
			os.makedirs(self.storage_path)
			log.info(utils.method.msg_kw(f"Created the session directory '{self.storage_path}'"))

	def __str__(self):
		return f"Session '{self.id}'"

	def __repr__(self):
		return f"Session('id={self.id}', 'root_path={self.root_path}')"
