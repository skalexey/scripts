from abc import ABC, ABCMeta, abstractmethod
from test import *

import utils.class_utils
import utils.class_utils as class_utils
import utils.function
import utils.method
from PySide6.QtWidgets import QApplication, QWidget


def init_test():
	log(title("Init Test"))
	class A:
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

	class B(A):
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

	class C:
		def __init__(self):
			log(utils.method.msg_kw())

	class D(A, C):
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

	class E:
		def __init__(self):
			log(utils.method.msg_kw())

	class F(A, E):
		def __init__(self):
			log(utils.method.msg_kw())
			A.__init__(self)
			E.__init__(self)
			super().__init__()
	log.expr("d = D()")
	log.expr("b = B()")
	log.expr("a = A()")
	log.expr("f = F()")
	log(title("End of Init Test"))
	
def abc_test():
	log(title("ABC Test"))
	app = QApplication([])
	class A(ABC):
		@abstractmethod
		def a(self):
			pass

	class B:
		pass

	class AbstractMethodNotDefined(A, B):
		pass

	class D(QWidget):
		pass

	try:
		class MetaclassConflictQt(A, D):
			pass
	except TypeError as e:
		log(f"Expected exception: {e}")

	assert_exception("amnd = AbstractMethodNotDefined()")

	class CustomMeta(type):
		pass

	try:
		class MetaclassConflict(ABC, metaclass=CustomMeta):
			pass
	except TypeError as e:
		log(f"Expected exception: {e}")

	class CombinedMeta(class_utils.EnforcedABCMeta, type(QWidget)):
		pass

	class F(ABC, metaclass=CombinedMeta):
		@abstractmethod
		def f(self):
			pass

	class G(F, QWidget):
		def a(self):
			log(utils.method.msg_kw())

	# Test to check if the abstract method enforcement works
	try:
		g = G()  # This should raise a TypeError
		assert False, "This should not be reached"
	except TypeError as e:
		log(f"Expected TypeError caught: {e}")

	log(title("End of ABC Test"))

def same_method_test():
	class A:
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()

		def f(self):
			log(utils.method.msg_kw())

	class B:
		def __init__(self):
			log(utils.method.msg_kw())

		def f(self):
			log(utils.method.msg_kw())

	class C(A, B):
		def __init__(self):
			log(utils.method.msg_kw())
			super().__init__()
	c = C()
	c.f()

def test():
	log(title("Inheritance Test"))
	# init_test()
	# abc_test()
	same_method_test()
	log(title("End of Inheritance Test"))

run()