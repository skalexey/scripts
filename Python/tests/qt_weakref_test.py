from test import *


def qt_weakref_test():
	import weakref

	from PySide6.QtWidgets import (
	    QApplication,
	    QGraphicsScene,
	    QGraphicsView,
	    QGraphicsWidget,
	)

	app = QApplication([])

	# Create a scene and a view
	scene = QGraphicsScene()
	view = QGraphicsView(scene)

	# Create a QGraphicsWidget and add it to the scene
	widget = QGraphicsWidget()
	scene.addItem(widget)

	# Create a weak reference to the widget
	widget_weak_ref = weakref.ref(widget)
	del widget

	assert widget_weak_ref() is not None

	# Now remove the widget from the scene and check the weak reference
	scene.removeItem(widget_weak_ref())

	assert widget_weak_ref() is None

	# Access the weak reference
	widget_ref = widget_weak_ref()

	if widget_ref is None:
		print("The widget was deleted.")
	else:
		print("The widget still exists.")

	view.show()
	app.exec()


def test():
	log(title("Qt Weakref Test"))
	qt_weakref_test()
	log(title("End of Qt Weakref Test"))

run()
