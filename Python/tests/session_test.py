import shutil
from test import *

from utils.session import Session


def session_test():
	log(title("Session Test"))
	# gc_test()
	integrity_test()
	log(title("End of Session Test"))

def integrity_test():
	shutil.rmtree("data/sessions/1", ignore_errors=True)
	shutil.rmtree("data/sessions/2", ignore_errors=True)
	shutil.rmtree("data/sessions/3", ignore_errors=True)
	shutil.rmtree("data/sessions/test_session_4", ignore_errors=True)
	s1 = Session(1, root_path="data/sessions")
	assert s1.a is None
	log.expr('s1.a = "i9j"')
	assert s1.a == "i9j"
	log.expr_and_val("s1.storage.a")
	log.expr('s1.storage.a = "fsd"')
	assert s1.storage.a == "fsd"
	log.expr_and_val("s1.storage.b")
	log.expr('s1.storage.b = 45')
	assert s1.storage.b == 45
	assert s1.id == '1'
	log.expr_and_val("s1.id")
	assert_exception("s1.id = 2")
	assert_exception("s1.storage.id = 2")
	log.expr_and_val("s1.id")

	s2 = Session(2, root_path="data/sessions")
	assert s2.id == '2'
	log.expr_and_val("s2.id")
	log.expr('s2.storage.c = "03249fs==-"')
	assert s2.storage.c == "03249fs==-"
	log.expr('s2.storage.d = 90094')
	assert s2.storage.d == 90094
	assert_exception("s2.id = 3")
	assert_exception("s2.storage.id = 3")
	log.expr_and_val("s2.id")

	s1.end()
	assert s1.id is None
	assert_exception("s1.id = 22")

	s2.end()
	assert s2.id is None
	log.expr_and_val("s2.id")
	assert_exception("s2.id = 33")
	assert_exception("s2.storage.id = 33")

	s3 = Session(3, root_path="data/sessions")
	log.expr_and_val("s3.id")

	s4 = Session(4, storage_path="data/sessions/test_session_4")
	assert s4.id == '4'

	s4_e = Session(4, storage_path="data/sessions/test_session_4")
	assert s4_e.id == '4'

	assert_exception('s5 = Session(5, storage_path="data/sessions/empty_directory")')
	
	class A:
		pass

	log.expr('s3.ca = A()')
	del s1
	del s2
	s3 = None
	s4 = None
	s4_e = None


def gc_test():
	class A:
		def __init__(self, s=None):
			log("A()")
			self.s = s or Session(1, root_path="data/sessions")
			# self.s.a = self

		def __repr__(self):
			return f"A({self.s})"
		
		def __del__(self):
			log(f"__del__({self})")

	class B:
		def __init__(self, s=None):
			log("B()")
			self.s = s or Session(1, root_path="data/sessions")
			self.s.b = self

		def __repr__(self):
			return f"B({self.s})"
		
		def __del__(self):
			log(f"__del__({self})")
		
	a = A()
	a2 = B(a.s)
	a.s.end()
	# a = None
	# a2 = None


def test():
	log(title("Test"))
	session_test()
	log(title("End of Test"))

run()
