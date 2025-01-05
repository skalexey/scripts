from utils.context import GlobalContext


class ApplicationContext(GlobalContext):
	"""
	Part of the module system, it serves as a hub for shared resources—such as settings_manager, plugin_manager, data_manager, session_manager, main_window, and the application instance—making them accessible to any module.
	"""

	is_live = False

	def __init__(self):
		self.settings_manager = None
		self.plugin_manager = None
		self.app = None
		self.main_window = None
		self.data_manager = None
		self.session_manager = None
		self._is_ready = False
		
	def is_ready(self):
		return self._is_ready

	def on_ready(self):
		self._is_ready = True
		self.module_manager.call_on_modules("on_context_ready")

	@classmethod
	def current_datetime(cls):
		return cls.app.current_datetime()

	@classmethod
	def current_time(cls):
		return cls.current_datetime().timestamp()
