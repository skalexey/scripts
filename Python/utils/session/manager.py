import os

import utils.file
import utils.function
import utils.pyside
from utils.collection.ordered_dict import OrderedDict

from .library import Session, SessionStorage


class SessionManager:
	def __init__(self, app_context, *args, **kwargs):
		self.app_context = app_context
		self._current_session = None
		self.storage_directory = os.path.join(app_context.data_manager.storage_directory, "sessions")
		self._session_list = self.load_session_list()
		super().__init__(*args, **kwargs)

	def load_session_list(self):
		session_list = OrderedDict()
		if os.path.exists(self.storage_directory):
			for bucket_id in os.listdir(self.storage_directory):
				bucket_dir = os.path.join(self.storage_directory, bucket_id)
				for subid in os.listdir(bucket_dir):
					session_id = f"{bucket_id}{subid}" if subid != "0" else bucket_id
					session_list[session_id] = os.path.join(bucket_dir, subid) # Just a list of session IDs with their paths initially. Sessions loaded by a request.
		return session_list
	
	# Creates a new session and sets it as the current.
	def new_session(self):
		bucket_id = self._session_bucket_id()
		storage_path = self._gen_session_path(bucket_id)
		session_id = self._session_id(storage_path)
		return self._inst_session(session_id, storage_path)

	# Loads a session and sets it as the current.
	def get_session(self, session_id):
		session = self._session_list.get(session_id)
		if not isinstance(session, (str, Session)):
			if isinstance(session, str):
				session = self._inst_session(storage_path=session)
			elif isinstance(session, SessionStorage):
				session = self._inst_session(storage=session)
			self._session_list[session_id] = session
		if session.id != session_id:
			raise ValueError(utils.function.msg("Unexpected error: The requested Session ID does not match the retrieved session object"))
		return session

	def get_session_storage(self, session_id):
		session_storage = self._session_list.get(session_id)
		if session_storage is None:
			return None
		if isinstance(session_storage, str):
			session_storage = SessionStorage(storage_path=session_storage)
			self._session_list[session_id] = session_storage
		elif isinstance(session_storage, Session):
			session_storage = session_storage.storage
		if session_storage.id != session_id:
			raise ValueError(utils.function.msg("Unexpected error: The requested Session ID does not match the retrieved session storage object"))
		return session_storage

	def current_session(self):
		return self._current_session

	def current_or_new_session(self):
		return self.current_session() or self.new_session()

	def screem_if_current_session(self):
		if self.current_session() is not None:
			utils.pyside.attention_message(message="There is already a current session. Close it before creating a new one, or create a Session object separately.")
			return True
		return False

	def _inst_session(self, *args, **kwargs):
		if self.screem_if_current_session():
			return None
		session = Session(*args, **kwargs)
		def on_session_end(self, session):
			if self.current_session() != session:
				raise ValueError(utils.function.msg("Session end event received from a session that is not the current session"))
			self._current_session = None
			self._session_list[session.id] = session.storage
			self.app_context.module_manager.call_on_modules("on_session_end", session)
		session.on_end.subscribe(on_session_end, self, caller=self)
		session_id = session.id
		self._session_list[session_id] = session
		self._current_session = session
		self.app_context.module_manager.call_on_modules("on_session_start", session)
		return session

	def _session_bucket_id(self):
		current_datetime = self.app_context.current_datetime()
		return current_datetime.strftime("%Y%m%d%H%M%S")

	def _gen_session_path(self, bucket_id):
		path = os.path.join(self.storage_directory, bucket_id)
		def gen_func(cnt):
			return os.path.join(path, f"{cnt}")
		return utils.file.gen_free_path(gen_func=gen_func)

	def _session_id(self, storage_path):
		relpath = os.path.relpath(storage_path, self.storage_directory)
		# The session id is concatenated path parts
		return relpath.replace(os.sep, "")
