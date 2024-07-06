from test import *

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

import utils.method
import utils.pyside


def super_test():
	class A:
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class B:
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class C:
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class D:
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class E(A, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class F(A, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super(B, self).__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class G:
		def __init__(self, a1, a2=None, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(a1, a2=a2, *args, **kwargs)
			log(utils.method.msg_kw("Post super"))
	
	class I(E, F):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class J(A, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class K(C, D):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class L(J, K):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class M(A, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			log("Calling A")
			# A.__init__(self, *args, **kwargs)
			# log("Calling B")
			# B.__init__(self, *args, **kwargs)
			# log("Calling super")
			# super().__init__(*args, **kwargs)

	class N(C, D):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class O(M, N):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class P:
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())

	class Q:
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class R(P, Q):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class S(A, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class T(R, S):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class U(QWidget, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class V(U, K):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			self.app = QApplication([])
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class W(A, B):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))
			# A.__init__(self, *args, **kwargs)
			# super(A, self).__init__(*args, **kwargs)

	class X(W, K):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class QA(QWidget, A):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class H(QWidget):
		def __init__(self, a1=None, a2=None, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(a1, *args, **kwargs)
			self.a2 = a2
			if a2 is not None:
				self.a2.addWidget(self)
				log(f"Added widget {self} to layout {a2}")

	class Y(H, QWidget):
		def __init__(self, a1=None, a2=None, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(a1, a2=a2, *args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class Z(Y, K):
		def __init__(self, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))
			# K.__init__(self, *args, **kwargs)

	class Receiver:
		def __init__(self, a1=None, a2=None, parent_layout=None, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(*args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	class Transition(QLabel, Receiver):
		def __init__(self, parent=None, *args, **kwargs):
			log(utils.method.msg_kw())
			super().__init__(parent, *args, **kwargs)
			log(utils.method.msg_kw("Post super"))

	log.expr("e = E()")
	log.expr("f = F()")
	log.expr("i = I()")
	log.expr("l = L()")
	log.expr("o = O()")
	log.expr("t = T()")
	log.expr("v = V()")
	log.expr("x = X()")
	log.expr("p = QWidget()")
	log.expr("layout = QVBoxLayout()")
	log.expr("z = Z(None, a2=None)")
	log.expr("list_widget = utils.pyside.ListWidget(parent_layout=layout)")
	log.expr("y = Y()")
	log.expr("layout.addWidget(y)")
	# log.expr("z.a2.addWidget(z)")
	log.expr("transition = Transition(parent=p, a2=layout, parent_layout=layout)")

	

def test():
	log(title("Super Test"))
	super_test()
	log(title("End of Super Test"))

run()
