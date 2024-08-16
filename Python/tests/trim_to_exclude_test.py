from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
)

import utils.pyside


class DraggableRect(QGraphicsRectItem):
	def __init__(self, rect, *args, **kwargs):
		super().__init__(rect, *args, **kwargs)
		self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

	def itemChange(self, change, value):
		if change == QGraphicsItem.ItemPositionChange:
			self.update_scene()
		return super().itemChange(change, value)

	def set_update_scene_callback(self, update_scene):
		self.update_scene = update_scene

def trim_to_exclude(rect1, rect2):
	if not rect1.intersects(rect2):
		return rect1

	intersection = rect1.intersected(rect2)

	# Calculate the areas of potential resulting rectangles
	top_area = QRectF(rect1.left(), rect1.top(), rect1.width(), intersection.top() - rect1.top()).height() * rect1.width()
	bottom_area = QRectF(rect1.left(), intersection.bottom() + 1, rect1.width(), rect1.bottom() - intersection.bottom()).height() * rect1.width()
	left_area = QRectF(rect1.left(), rect1.top(), intersection.left() - rect1.left(), rect1.height()).width() * rect1.height()
	right_area = QRectF(intersection.right() + 1, rect1.top(), rect1.right() - intersection.right(), rect1.height()).width() * rect1.height()

	# Determine which resulting rectangle has the maximum area
	max_area = max(top_area, bottom_area, left_area, right_area)

	if max_area == top_area:
		rect1.setBottom(intersection.top() - 1)
	elif max_area == bottom_area:
		rect1.setTop(intersection.bottom() + 1)
	elif max_area == left_area:
		rect1.setRight(intersection.left() - 1)
	else:
		rect1.setLeft(intersection.right() + 1)

	return rect1

class TrimToExcludeView(QGraphicsView):
	def __init__(self, parent, scene, rect1, rect2):
		super().__init__(parent)
		self.setScene(scene)
		self.rect1_item = QGraphicsRectItem(rect1)
		self.rect2_item = DraggableRect(rect2)

		self.rect1_item.setPen(QPen(Qt.black, 2))
		self.rect1_item.setBrush(QColor(200, 200, 255, 100))

		self.rect2_item.setPen(QPen(Qt.red, 2))
		self.rect2_item.setBrush(QColor(255, 200, 200, 100))

		self.scene().addItem(self.rect1_item)
		self.scene().addItem(self.rect2_item)

		self.trimmed_item = QGraphicsRectItem()
		self.trimmed_item.setPen(QPen(Qt.green, 2))
		self.trimmed_item.setBrush(QColor(200, 255, 200, 150))
		self.scene().addItem(self.trimmed_item)

		self.rect2_item.set_update_scene_callback(self.update_trimmed_rect)
		self.update_trimmed_rect()

	def update_trimmed_rect(self):
		rect1 = self.rect1_item.rect()
		rect2 = self.rect2_item.sceneBoundingRect()
		# trimmed_rect = trim_to_exclude(QRectF(rect1), rect2)
		trimmed_rect = utils.pyside.reduce_rect_2(QRectF(rect1), rect2)
		self.trimmed_item.setRect(trimmed_rect)

def main():
	app = QApplication([])

	scene = QGraphicsScene()

	rect1 = QRectF(100, 100, 200, 150)
	rect2 = QRectF(150, 120, 100, 100)

	view = TrimToExcludeView(None, scene, rect1, rect2)
	view.setRenderHint(QPainter.Antialiasing)
	view.setGeometry(100, 100, 800, 600)
	view.show()

	app.exec()

if __name__ == "__main__":
	main()
