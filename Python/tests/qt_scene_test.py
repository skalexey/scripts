from test import *

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)


def qt_scene_test():
	from PySide6.QtGui import QBrush, QPalette, QPen

	class DraggableRect(QGraphicsRectItem):
		def __init__(self, *args):
			super().__init__(*args)
			self.setFlag(QGraphicsRectItem.ItemIsMovable)
			self.setFlag(QGraphicsRectItem.ItemSendsScenePositionChanges)

		def itemChange(self, change, value):
			if change == QGraphicsRectItem.ItemPositionChange:
				scene = self.scene()
				if scene:
					scene.setSceneRect(scene.itemsBoundingRect())
					update_scene_geometry_text(scene)
			return super().itemChange(change, value)


	def update_scene_geometry_text(scene):
		scene_rect = scene.sceneRect()
		x, y, w, h = scene_rect.x(), scene_rect.y(), scene_rect.width(), scene_rect.height()
		formatted_rect = f"({x:.2f}, {y:.2f}, {w:.2f}, {h:.2f})"
		text.setText(f'Scene Geometry: {formatted_rect}')
		text_width = text.boundingRect().width()
		text_height = text.boundingRect().height()
		text.setPos(scene_rect.right() - text_width - 10, scene_rect.bottom() - text_height - 10)

	app = QApplication([])

	# Create the scene and the view
	scene = QGraphicsScene()
	view = QGraphicsView(scene)
	view.setSceneRect(0, 0, 400, 400)

	# Set scrollbars to appear as needed
	view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
	view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

	# Use palette colors to adapt to light/dark themes
	palette = app.palette()

	# Create a draggable rectangle item
	rect_item = DraggableRect(0, 0, 100, 100)
	pen = QPen(palette.color(QPalette.Text))
	brush = QBrush(palette.color(QPalette.Base))
	rect_item.setPen(pen)
	rect_item.setBrush(brush)
	scene.addItem(rect_item)

	# Create a text item to display scene geometry
	text = QGraphicsSimpleTextItem()
	text.setBrush(QBrush(palette.color(QPalette.Text)))
	scene.addItem(text)

	# Initially update the scene geometry text
	update_scene_geometry_text(scene)

	view.show()
	app.exec()




def test():
	log(title("Qt Scene Test"))
	qt_scene_test()
	log(title("End of Qt Scene Test"))

run()
