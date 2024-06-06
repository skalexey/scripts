import sys

import utils.log
import utils.module

logger = utils.log.Logger("test_module")

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
	logger.log("Test 1")
	m = Module()
	logger.log(m.test_setting)
	m.test_setting = 5
	logger.log(m.test_setting)
	# logger.log_expr("m=Module()", globals(), locals())
	# logger.log_expr("print(m.test_setting)", globals(), locals())
	# logger.log_expr("m.test_setting=5", globals(), locals())
	# logger.log_expr("print(m.test_setting)", globals(), locals())

def test2():
	logger.log("Test 2")
	m = Module2()
	logger.log(m.test_setting_2)
	m.test_setting_2 = 5
	logger.log(m.test_setting_2)

def test():
	test1()
	test2()

function_name = sys.argv[1] if len(sys.argv) > 1 else "test"
locals()[function_name]()
