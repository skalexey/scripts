import sys

import utils.module
from utils.log.logger import Logger

log = Logger()

class Module(utils.module.Module):
	def __init__(self):
		super().__init__("test_module")
		self.define_setting("test_setting", 0)

	def on_test_setting_changed(self, value):
		print(f"on_test_setting_changed({value})")

	def on_test_setting_set(self, value):
		print(f"on_test_setting_set({value})")

class Module2(utils.module.Module):
	def __init__(self):
		super().__init__("test_module")
		self.define_setting("test_setting_2", 0)

	def set_test_setting(self, value):
		self._set_defined_setting_by_name_base("test_setting_2", value)
		print(f"test_setting={value}")
	
def test1():
	log("Test 1")
	m = Module()
	log(m.test_setting)
	m.test_setting = 5
	log(m.test_setting)
	# log.expr("m=Module()", globals(), locals())
	# log.expr("print(m.test_setting)", globals(), locals())
	# log.expr("m.test_setting=5", globals(), locals())
	# log.expr("print(m.test_setting)", globals(), locals())

def test2():
	log("Test 2")
	m = Module2()
	log(m.test_setting_2)
	m.test_setting_2 = 5
	log(m.test_setting_2)

def test():
	test1()
	test2()

function_name = sys.argv[1] if len(sys.argv) > 1 else "test"
locals()[function_name]()
