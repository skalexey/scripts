import utils.pyside
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


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

class TrimToExcludeView(QGraphicsView):
	def __init__(self, rect1, rect2, *args, **kwargs):
		super().__init__(*args, **kwargs)
		scene = QGraphicsScene()
		self.setScene(scene)
		self.setRenderHint(QPainter.Antialiasing)
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
		trimmed_rect = utils.pyside.reduce_rect_max(QRectF(rect1), rect2)
		self.trimmed_item.setRect(trimmed_rect)

class SubtractRectsView(QGraphicsView):
	def __init__(self, rect1, rect2, *args, **kwargs):
		super().__init__(*args, **kwargs)
		scene = QGraphicsScene()
		self.setScene(scene)
		self.setRenderHint(QPainter.Antialiasing)
		self.rect1_item = QGraphicsRectItem(rect1)
		self.rect2_item = DraggableRect(rect2)

		self.rect1_item.setPen(QPen(Qt.black, 2))
		self.rect1_item.setBrush(QColor(200, 200, 255, 100))

		self.rect2_item.setPen(QPen(Qt.red, 2))
		self.rect2_item.setBrush(QColor(255, 200, 200, 100))

		self.scene().addItem(self.rect1_item)
		self.scene().addItem(self.rect2_item)

		self.resulting_items = []
		self.rect2_item.set_update_scene_callback(self.update_subtracted_rects)
		self.update_subtracted_rects()

	def update_subtracted_rects(self):
		rect1 = self.rect1_item.rect()
		rect2 = self.rect2_item.sceneBoundingRect()
		resulting_rects = utils.pyside.subtract_rects(QRectF(rect1), rect2)
		
		for item in self.resulting_items:
			self.scene().removeItem(item)
		self.resulting_items.clear()

		for r in resulting_rects:
			item = QGraphicsRectItem(r)
			item.setPen(QPen(Qt.green, 2))
			item.setBrush(QColor(200, 255, 200, 150))
			self.scene().addItem(item)
			self.resulting_items.append(item)

class TestWindow(QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("QRect Operations Test")

		self.layout = QVBoxLayout(self)

		self.btn_trim = QPushButton("Trim To Exclude Test")
		self.btn_subtract = QPushButton("Subtract Rects Test")

		self.btn_trim.clicked.connect(self.show_trim_test)
		self.btn_subtract.clicked.connect(self.show_subtract_test)

		self.layout.addWidget(self.btn_trim)
		self.layout.addWidget(self.btn_subtract)

		self.trim_view = TrimToExcludeView(QRectF(100, 100, 200, 150), QRectF(150, 120, 100, 100), parent=self)
		self.subtract_view = SubtractRectsView(QRectF(100, 100, 200, 150), QRectF(150, 120, 100, 100), parent=self)

		self.layout.addWidget(self.trim_view)
		self.layout.addWidget(self.subtract_view)

		self.trim_view.hide()
		self.subtract_view.hide()

	def show_trim_test(self):
		self.trim_view.show()
		self.subtract_view.hide()

	def show_subtract_test(self):
		self.trim_view.hide()
		self.subtract_view.show()

def main():
	app = QApplication([])

	window = TestWindow()
	window.resize(800, 800)
	window.show()

	app.exec()

if __name__ == "__main__":
	main()
