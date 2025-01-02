import gc
import types
from functools import partial
from test import *

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from utils.application_context import ApplicationContext
from utils.memory import SmartCallable, weak_self_class, weak_self_method
from utils.profile.trackable_resource import TrackableResource
from utils.profile.weakref_manager import WeakrefManager
from utils.pyside import WidgetBase
from utils.pyside.application import Application


class TestApplication(Application):
	def on_update(self, dt):
		pass

app_context = ApplicationContext()
app = TestApplication(app_context, [])
app_context.app = app
window = QMainWindow()
window.setWindowTitle("Qt Test")
layout = QVBoxLayout()
central_widget = QWidget()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

def qt_test():
	# multiple_values_test()
	# circular_ref_test()
	# geometry_test()
	zero_qrectf_test()
	# scene_widget_test()
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

def geometry_test():
	log(title("Geometry Test"))
	no_layout_widget_test()
	layout_widget_test()
	log(title("End of Geometry Test"))

def no_layout_widget_test():
	log(title("No Layout Widget Test"))
	w1 = QWidget()
	window.centralWidget().layout().addWidget(w1)
	assert w1.size() == QSize(640, 480), "w1.size() should be of the default size QSize(640, 480)"
	w1.adjustSize()
	w1.adjustSize()
	w1.adjustSize()
	assert w1.size() == QSize(640, 480), "w1.size() should still be of the default size QSize(640, 480) since there are no children"
	for i in range(15):
		btn = QPushButton(f"Button {i}", w1)
		btn.move(i * 50, i * 50)
		log(f"Button {i}: {btn.geometry()}")
	l1 = QLabel("Label 1", w1)
	log(f"Label 1: {l1.geometry()}")
	log(f"w1: geometry={w1.geometry()}, rect={w1.rect()}, frameGeometry={w1.frameGeometry()}, childrenRect={w1.childrenRect()}, contentsRect={w1.contentsRect()}, sizeHint={w1.sizeHint()}")
	assert not w1.geometry().contains(w1.childrenRect()), "w1.geometry() should be less than w1.childrenRect()"
	w1.adjustSize()
	assert w1.size() != QSize(640, 480), "w1.size() should not be QSize(640, 480) after adjustSize()"
	assert w1.geometry().contains(w1.childrenRect()), "w1.geometry() should be equal to w1.childrenRect()"
	assert w1.geometry() == w1.childrenRect(), "w1.geometry() should be equal to w1.childrenRect()"
	log(f"w1 after adjustSize(): geometry={w1.geometry()}, rect={w1.rect()}, frameGeometry={w1.frameGeometry()}, childrenRect={w1.childrenRect()}, contentsRect={w1.contentsRect()}, sizeHint={w1.sizeHint()}")
	log(title("End of No Layout Widget Test"))

def layout_widget_test():
	log(title("Layout Widget Test"))
	w1 = QWidget()
	window.centralWidget().layout().addWidget(w1)
	layout = QVBoxLayout()
	w1.setLayout(layout)
	assert w1.size() == QSize(640, 480), "w1.size() should still be of default size QSize(640, 480)"
	l1 = QLabel("Label 1")
	layout.addWidget(l1)
	assert w1.size() == QSize(640, 480), "w1.size() should still be of default size QSize(640, 480)"
	log(f"w1: geometry={w1.geometry()}, rect={w1.rect()}, frameGeometry={w1.frameGeometry()}, childrenRect={w1.childrenRect()}, contentsRect={w1.contentsRect()}, sizeHint={w1.sizeHint()}")
	w1.adjustSize()
	assert w1.size() != QSize(640, 480), "w1.size() should not be QSize(640, 480) after adjustSize()"
	log(title("End of Layout Widget Test"))

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

	man = WeakrefManager()
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

def scene_widget_test():
	from PySide6.QtWidgets import (
	    QApplication,
	    QGraphicsLineItem,
	    QGraphicsRectItem,
	    QGraphicsScene,
	    QGraphicsView,
	    QGraphicsWidget,
	)

	class MyGraphicsWidget(QGraphicsWidget):
		def __init__(self):
			super().__init__()
			rect_item = QGraphicsRectItem(parent=self)
			rect_item.setRect(0, 0, 100, 100)
			rect_item.setPos(1, 2)
			self.rect_item = rect_item
			line_item = QGraphicsLineItem(parent=self)
			line_item.setLine(0, 0, 100, 100)
			line_item.setPos(10, 20)
			self.line_item = line_item

	scene = QGraphicsScene()
	view = QGraphicsView(scene)
	view.setGeometry(100, 100, 800, 600)
	assert scene.items() == [], "scene.items() should be empty"
	widget = MyGraphicsWidget()
	scene.addItem(widget)
	items = scene.items()
	for item in items:
		log(f"item: {item}")
	assert items == [widget.line_item, widget.rect_item, widget], "scene.items() should contain widget and the rect_item as well"
	widget_child_items = widget.childItems()
	assert widget_child_items == [widget.rect_item, widget.line_item], "widget.childItems() should contain the line_item and rect_item"

def zero_qrectf_test():
	log(title("Zero QRectF Test"))
	from PySide6.QtCore import QRectF
	zero_rect = QRectF(0, 0, 0, 0)
	assert zero_rect.isEmpty(), "zero_rect should be empty"
	assert zero_rect.isNull(), "zero_rect should be null"
	assert not zero_rect, "zero_rect should be falsy"
	assert not bool(zero_rect), "zero_rect should be falsy"
	log(title("End of Zero QRectF Test"))

def test():
	log(title("Qt Test"))
	qt_test()
	log(title("End of Qt Test"))

run()
