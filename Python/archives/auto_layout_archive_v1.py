from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLayout,
    QLayoutItem,
    QPushButton,
    QRect,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QWidgetItem,
)


class AutoLayout(QLayout):
	def __init__(self, parent=None, margin=0, spacing=-1):
		super().__init__(parent)
		self._items = []
		self.setContentsMargins(margin, margin, margin, margin)
		self.setSpacing(spacing if spacing >= 0 else self.spacing())

	def addItem(self, item):
		if not isinstance(item, QLayoutItem):
			raise TypeError("item must be a QLayoutItem")
		self._items.append(item)

	def addLayout(self, layout):
		self.addItem(layout)

	def sizeHint(self):
		return self.minimumSize()

	def minimumSize(self):
		size = QSize()
		for item in self._items:
			size = size.expandedTo(item.minimumSize())
		size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
		return size

	def count(self):
		return len(self._items)

	def itemAt(self, index):
		if index >= 0 and index < len(self._items):
			return self._items[index]
		return None

	def takeAt(self, index):
		if index >= 0 and index < len(self._items):
			return self._items.pop(index)
		return None

	def expandingDirections(self):
		return Qt.Orientations(Qt.Horizontal | Qt.Vertical)

	def hasHeightForWidth(self):
		return True

	def heightForWidth(self, width):
		return self.doLayout(QRect(0, 0, width, 0), True)

	def setGeometry(self, rect):
		super().setGeometry(rect)
		self.doLayout(rect, False)

	def doLayout(self, rect, testOnly):
		x = rect.x()
		y = rect.y()
		lineHeight = 0

		for item in self._items:
			if item is None:
				continue

			sizeHint = item.sizeHint()
			if sizeHint.isEmpty() and item.layout():
				sizeHint = self.calculateLayoutSizeHint(item.layout())

			spaceX, spaceY = self.calculateSpacing(item)
			nextX = x + sizeHint.width() + spaceX

			if nextX - spaceX > rect.right() and lineHeight > 0:
				x = rect.x()
				y = y + lineHeight + spaceY
				nextX = x + sizeHint.width() + spaceX
				lineHeight = 0

			if not testOnly:
				if item.widget():
					item.setGeometry(QRect(QPoint(x, y), sizeHint))
				elif item.layout():
					# Set parent for all widgets in the nested layout
					for i in range(item.layout().count()):
						nested_item = item.layout().itemAt(i)
						if nested_item.widget():
							nested_item.widget().setParent(self.parentWidget())
					item.layout().setGeometry(QRect(QPoint(x, y), sizeHint))

			x = nextX
			lineHeight = max(lineHeight, sizeHint.height())

		return y + lineHeight - rect.y()

	def calculateSpacing(self, item):
		if item.widget() is not None:
			wid = item.widget()
			spaceX = self.spacing() + wid.style().layoutSpacing(
				QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
			spaceY = self.spacing() + wid.style().layoutSpacing(
				QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
		elif item.layout() is not None:
			spaceX = self.spacing()
			spaceY = self.spacing()
		else:
			spaceX = 0
			spaceY = 0
		return spaceX, spaceY

	def calculateLayoutSizeHint(self, layout):
		size = QSize(0, 0)
		for i in range(layout.count()):
			item = layout.itemAt(i)
			if item:
				size = size.expandedTo(item.sizeHint())
		size += QSize(2 * layout.contentsMargins().left(), 2 * layout.contentsMargins().top())
		return size

# Example usage
if __name__ == "__main__":
	import sys
	app = QApplication(sys.argv)

	parent_widget = QWidget()
	layout = AutoLayout(parent_widget)
	parent_widget.setLayout(layout)

	# Create and add some child widgets
	for i in range(10):
		button = QPushButton(f"Button {i + 1}")
		layout.addWidget(button)

	# Create and add a nested layout
	nested_layout = QVBoxLayout()
	nested_layout.addWidget(QPushButton("Nested Button 1"))
	nested_layout.addWidget(QPushButton("Nested Button 2"))
	layout.addLayout(nested_layout)

	parent_widget.show()
	sys.exit(app.exec())
