import utils.pyside
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
)


def visualize_rects(rect1, rect2, subtracted_rects):
	app = QApplication([])

	scene = QGraphicsScene()
	view = QGraphicsView(scene)

	# Original Rectangles
	rect1_item = QGraphicsRectItem(rect1)
	rect1_item.setPen(QPen(Qt.black, 2))
	rect1_item.setBrush(QColor(200, 200, 255, 100))

	rect2_item = QGraphicsRectItem(rect2)
	rect2_item.setPen(QPen(Qt.red, 2))
	rect2_item.setBrush(QColor(255, 200, 200, 100))

	scene.addItem(rect1_item)
	scene.addItem(rect2_item)

	# Subtracted Rectangles
	for r in subtracted_rects:
		item = QGraphicsRectItem(r)
		item.setPen(QPen(Qt.green, 2))
		item.setBrush(QColor(200, 255, 200, 150))
		scene.addItem(item)

	view.setRenderHint(QPainter.Antialiasing)
	view.setGeometry(100, 100, 800, 600)
	view.show()

	app.exec()

# Example Usage
rect1 = QRectF(100, 100, 200, 150)
rect2 = QRectF(150, 120, 100, 100)

subtracted_rects = utils.pyside.subtract_rects(rect1, rect2)
visualize_rects(rect1, rect2, subtracted_rects)
