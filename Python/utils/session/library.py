import os

import utils.lang
import utils.method
import utils.serialize
from utils.intrstate import Intrstate
from utils.log.logger import Logger
from utils.profile.trackable_resource import TrackableResource
from utils.subscription import Subscription

log = Logger()

class SessionStorage(Intrstate):
	fname = "session.json"
	# Session creates a directory in root_path named with the id for all the data.
	def __init__(self, id=None, storage_path=None, root_path=None, *args, **kwargs):
		log.debug(utils.method.msg_kw(f"Creating a session storage"))
		_id = str(id) if id is not None else None
		if _id is None and storage_path is None:
			raise ValueError(utils.method.msg_kw("Either 'id' or 'storage_path' must be provided"))
		if root_path is None and storage_path is None is None:
			raise ValueError(utils.method.msg_kw("Either 'root_path' or 'storage_path' must be provided"))
		self.path = os.path.normpath(storage_path or os.path.join(root_path, _id))
		# All the attributes will be stored in the state since this moment.
		if os.path.exists(self.path):
			log.info(utils.method.msg_kw(f"Already exists. It will use the existing resources."))
			state = self._load()
			if state is None:
				raise ValueError(utils.method.msg_kw(f"Failed to load the session storage from '{self.path}'"))
			# Make the ID field protected
			loaded_id = state.get('id')
			if _id is not None:
				if _id != loaded_id:
					raise ValueError(utils.method.msg_kw(f"Session ID mismatch: '{_id}' != '{loaded_id}'"))
			self.id = loaded_id # Store ID to the private section
			self._state = state
		else:
			log.info(utils.method.msg_kw(f"Creating a new session storage at '{self.path}'."))
			if _id is None:
				raise ValueError(utils.method.msg_kw("Session ID was not provided for a new session storage"))
			self.id = _id # Store ID to the private section
			os.makedirs(self.path)
			log.info(utils.method.msg_kw(f"Created the session directory '{self.path}'"))
			state = {'id': self.id}
			self._state = state
			self._store()
		super().__init__(*args, **kwargs)
				
	def __str__(self):
		return f"SessionStorage(storage_path='{self.path}')"

	def __repr__(self):
		return self.__str__()

	def _on_state_update(self, name, value):
		self._store()
		
	def _store(self):
		if not self.path:
			return False
		fpath = os.path.join(self.path, self.fname)
		utils.serialize.to_json(self._state, fpath=fpath)
		log.debug(utils.function.msg_kw(f"Stored the session to '{fpath}'"))
		return True

	def _load(self):
		fpath = os.path.join(self.path, self.fname)
		log.debug(utils.function.msg_kw(f"Loading the session storage from '{fpath}'"))
		if not os.path.exists(fpath):
			log.warning(utils.function.msg_kw(f"Session file '{fpath}' does not exist"))
			return None
		deserialize_result = utils.serialize.from_json(fpath=fpath)
		if deserialize_result is None:
			raise Exception(utils.function.msg_kw(f"Failed to load the session from '{fpath}'"))
		log.debug(utils.function.msg_kw(f"Loaded the session storage from '{fpath}'"))
		return deserialize_result

class Session(TrackableResource, Intrstate):
	def __init__(self, id=None, storage_path=None, root_path=None, storage=None, *args, **kwargs):
		log.info(utils.method.msg_kw(f"Creating a session"))
		self.storage = storage or SessionStorage(id, storage_path, root_path)
		self.on_end = Subscription()
		super().__init__(*args, **kwargs)

	@property
	def id(self):
		return self.storage.id if self.storage is not None else None

	def __str__(self):
		return f"Session '{self.id}'"

	def __repr__(self):
		return f"Session('id={self.id}', 'storage path: {self.storage.path if self.storage is not None else None}')"

	def __bool__(self):
		return self.on_end is not None

	def end(self):
		log.info(utils.function.msg_kw())
		if self.on_end is None:
			raise ValueError(utils.function.msg_v(f"Session has already been ended"))
		on_end = self.on_end
		self.__dict__["on_end"] = None
		on_end.notify(self)
		utils.lang.clear_resources(self._state)
		utils.lang.clear_resources(self)
		log.info(utils.function.msg_kw(f"Session has been ended"))
