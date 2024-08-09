import weakref

import utils.memory
import utils.method
from utils.collection.ordered_dict import OrderedDict
from utils.log.logger import Logger

log = Logger()

class ModuleManager:
	def __init__(self, modules_dir):
		self.modules = OrderedDict()

	def register_module(self, name, module):
		existing_module = self.modules.get(name)
		if existing_module is not None:
			return False
			raise Exception(f"Trying to register a module '{name}' that is already registered")
		def delete_if_dead(ref, self_weak=utils.memory.weak_proxy(self), name=name):
			log.warning(f"Unregistering module '{name}' upon deletion of the reference")
			assert ref() is None
			if not self_weak.is_alive():
				return
			current_ref = self_weak.modules.get(name)
			# Check if the new one is not already there
			if current_ref == ref:
				del self_weak.modules[name]
		self.modules[name] = weakref.ref(module, delete_if_dead)
		return True

	def unregister_module(self, name):
		if name in self.modules:
			del self.modules[name]
			return True
		return False

	def call_on_module(self, module, method_name, *args, **kwargs):
		attr = getattr(module, method_name, None)
		if attr is not None:
			return attr(*args, **kwargs)
		return None

	def call_on_modules(self, method_name, *args, **kwargs):
		log.verbose(utils.method.msg(f"Calling method '{method_name}' on all modules"))
		results = []
		for ref in self.modules.values():
			module = ref()
			result = self.call_on_module(module, method_name, *args, **kwargs)
			results.append(result)
		return results

	def get_module(self, name):
		ref = self.modules.get(name)
		return ref()
