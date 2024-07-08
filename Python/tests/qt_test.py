import gc
import types
from functools import partial
from test import *

from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from utils.application_context import ApplicationContext
from utils.memory import SmartCallable, weak_self_class, weak_self_method
from utils.profile.refmanager import RefManager
from utils.profile.trackable_resource import TrackableResource
from utils.pyside import WidgetBase
from utils.pyside.application import Application


class TestApplication(Application):
	def on_update(self, dt):
		pass

app_context = ApplicationContext()
app = TestApplication(app_context, [])
window = QMainWindow()
window.setWindowTitle("Circular Reference Test")
layout = QVBoxLayout()
central_widget = QWidget()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

def qt_test():
	multiple_values_test()
	circular_ref_test()
	window.show()
	log("app.exec()")
	app.exec()


def TrackableWidget(base_class):
	class TrackableWidget(WidgetBase(TrackableResource, base_class)):
		pass
	return TrackableWidget


def multiple_values_test():
	class ChildOwner(TrackableResource):
		def __init__(self, parent):
			super().__init__()
			assert_exception('self.button = TrackableWidget(QPushButton)("Click me!", parent, parent=parent)')
	
	c = ChildOwner(window)


def circular_ref_test():
	log(title("Circular Reference Test"))
	# Don't use log.expr for resources whose lifetime needs to be tracked since it exposes objects to another stack frame and undermines the outcome of this test


	class ChildOwner(TrackableResource):
		def __init__(self, parent):
			super().__init__()
			self.capture_self(parent)
			# assert_exception('self.button = TrackableWidget(QPushButton)("Click me!", parent, parent=parent)')
			# self.layout = QVBoxLayout(parent)

		def create_closure(self, parent):
			button = TrackableWidget(QPushButton)(self.__class__.__name__)
			parent.layout().addWidget(button)
			return button

		def capture_self(self, parent):
			return self.create_closure(parent)

	class Composition(ChildOwner):
		def capture_self(self, parent):
			self.c = self.create_closure(parent)
			return self.c

	class ConnectedComposition(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			button.clicked.connect(self._on_click)
			return button

		def _on_click(self):
			log(utils.method.msg("Button clicked"))

	class ConnectedFunc(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			def on_click():
				log(utils.method.msg(f"Capturing self: {self}"))
			button.clicked.connect(on_click)
			return button

	class ConnectedFuncNoCapture(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			def on_click():
				log(utils.method.msg(f"No capture func"))
			button.clicked.connect(on_click)
			return button

	class ConnectedFuncComposition(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			def on_click():
				log(utils.method.msg(f"Capturing self: {self}"))
			button.clicked.connect(on_click)
			return on_click

	class ConnectedFuncCompositionWeakSelf(Composition):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.value = 444

		def create_closure(self, parent):
			button = Composition.create_closure(self, parent)
			def on_click():
				try:
					log(utils.method.msg(f"Capturing self: {self.value}"))
				except ReferenceError as e:
					log(utils.method.msg(f"ReferenceError: {e}"))
			button.clicked.connect(on_click)
			return on_click

	@weak_self_class
	class ConnectedFuncCompositionWeakSelfClass(ConnectedFuncCompositionWeakSelf):
		def create_closure(self, parent):
			return ConnectedFuncCompositionWeakSelf.create_closure(self, parent)

	class ConnectedFuncCompositionWeakSelfMethod(ConnectedFuncCompositionWeakSelf):
		@weak_self_method
		def create_closure(self, parent):
			return ConnectedFuncCompositionWeakSelf.create_closure(self, parent)

	class CapturedWidget(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			w = QWidget()
			parent.layout().addWidget(w)
			def on_click():
				log(utils.method.msg(f"Capturing widget {w}"))
			button.clicked.connect(on_click)
			return button
		
	class BoundArguments(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			f = partial(self.p, 3)
			button.clicked.connect(f)
			return button
		
		def p(self, a):
			log(utils.method.msg_kw(f"self: {self}"))

	class DynamicMethod(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			def m(self):
				log(utils.method.msg(f"Dynamic method capturing self: {self}"))
			method = types.MethodType(m, self)
			button.clicked.connect(method)
			return button
		
	class SmartCallableComposition(Composition):
		def create_closure(self, parent):
			button = super().create_closure(parent)
			sc = SmartCallable(self.scm)
			button.clicked.connect(sc)
			return button
		
		def scm(self):
			log(utils.method.msg(f"capturing self: {self}"))

	man = RefManager()
	def closed_scope(window, central_widget):
		log(title("Closed scope"))
		man.child_owner = ChildOwner(central_widget)
		man.composition = Composition(central_widget)
		man.connected_composition = ConnectedComposition(central_widget)
		man.connected_func = ConnectedFunc(central_widget)
		man.connected_func_no_capture = ConnectedFuncNoCapture(central_widget)
		man.connected_func_composition = ConnectedFuncComposition(central_widget)
		man.connected_func_composition_weak_self_class = ConnectedFuncCompositionWeakSelfClass(central_widget)
		man.connected_func_composition_weak_self_method = ConnectedFuncCompositionWeakSelfMethod(central_widget)
		man.captured_widget = CapturedWidget(central_widget)
		man.bound_arguments = BoundArguments(central_widget)
		man.dynamic_method = DynamicMethod(central_widget)
		man.smart_callable = SmartCallableComposition(central_widget)
		log(title("End of Closed scope"))

	closed_scope(window, central_widget)

	assert man.child_owner is None, "ChildOwner should have been collected since it has no reference to itself"
	assert man.composition is None, "Composition should have been collected since it has no reference to itself"
	assert man.connected_composition is None, "ConnectedComposition should have been collected since it has no reference to itself"
	assert man.connected_func is not None, "ConnectedFunc should have not been collected since it has a reference to itself captured by .connect()"
	assert man.connected_func_no_capture is None, "ConnectedFuncNoCapture should have been collected since it has no reference to itself"
	assert man.connected_func_composition is not None, "ConnectedFuncComposition should have not been collected since it has a reference to itself captured by .connect()"
	assert man.connected_func_composition_weak_self_class is None, "ConnectedFuncCompositionWeakSelf should have been collected since it has no strong reference to itself"
	assert man.connected_func_composition_weak_self_method is None, "ConnectedFuncCompositionWeakMethod should have been collected since it has no strong reference to itself"
	assert man.captured_widget is None, "CapturedWidget should have been collected since it has no reference to itself"
	gc.collect()
	gc.collect()
	assert man.connected_func is not None, "ConnectedFunc should have not been collected since it has a reference to itself captured by .connect() and the widget is still alive"
	man.connected_func.c.deleteLater()
	assert man.connected_func is not None, "ConnectedFunc should have not been collected since it has a reference to itself captured by .connect() and the widget is still alive"
	gc.collect()
	gc.collect()
	assert man.connected_func is not None, "ConnectedFunc should have not been collected since it has a reference to itself captured by .connect() and the widget is still alive"
	time_elapsed = 0
	def check(dt):
		nonlocal time_elapsed
		time_elapsed += dt
		if time_elapsed > 1:
			assert man.connected_func is None, "ConnectedFunc should have been collected now"
			log("ConnectedFunc has been collected")
			return False
	app.add_on_update(check)
	assert man.bound_arguments is not None, "BoundArguments should have not been collected since it has a reference to itself inside a function that is the result of partial() captured by .connect()"
	assert man.dynamic_method is None, "DynamicMethod should have been collected since it has no reference to itself"
	assert man.smart_callable is None, "SmartCallable should have been collected since it has no reference to itself"
	log(title("End of Circular Reference Test"))

def test():
	log(title("Qt Test"))
	qt_test()
	log(title("End of Qt Test"))

run()