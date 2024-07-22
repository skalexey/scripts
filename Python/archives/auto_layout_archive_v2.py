class ItemInfo:
	def __init__(self, item, new_row=False):
		self.item = item
		self.new_row = new_row

class AutoLayout(QLayout):
	def __init__(self, parent=None, margin=0, spacing=-1):
		super().__init__(parent)
		self._items = []
		self.setContentsMargins(margin, margin, margin, margin)
		self.setSpacing(spacing if spacing >= 0 else self.spacing())

	def addWidget(self, widget, new_row=False):
		super().addWidget(widget)
		item = self.itemAt(self.count() - 1)
		assert item.widget() == widget
		self._items[-1].new_row = new_row

	def addItem(self, item, new_row=False):
		if not isinstance(item, QLayoutItem):
			raise TypeError("item must be a QLayoutItem")
		self._items.append(ItemInfo(item, new_row))

	def _update_item_parent(self, item):
		if item.widget():
			item.widget().setParent(self.parentWidget())
		elif item.layout():
			for i in range(item.layout().count()):
				nested_item = item.layout().itemAt(i)
				self._update_item_parent(nested_item)

	def addLayout(self, layout, new_row=False):
		self.addItem(layout, new_row)
		self._update_item_parent(layout)

	def sizeHint(self):
		return self.minimumSize()

	def minimumSize(self):
		size = QSize()
		for item_info in self._items:
			size = size.expandedTo(item_info.item.minimumSize())
		size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
		return size

	def count(self):
		return len(self._items)

	def itemAt(self, index):
		if index >= 0 and index < len(self._items):
			return self._items[index].item
		return None

	def takeAt(self, index):
		if index >= 0 and index < len(self._items):
			return self._items.pop(index).item
		return None

	def expandingDirections(self):
		return Qt.Orientations(Qt.Horizontal | Qt.Vertical)

	def hasHeightForWidth(self):
		return True

	def heightForWidth(self, width):
		return self._do_layout(QRect(0, 0, width, 0), True)

	def setGeometry(self, rect):
		super().setGeometry(rect)
		self._do_layout(rect, False)

	def _do_layout(self, rect, test_only):
		x = rect.x()
		y = rect.y()
		row_height = 0
		row_items = []

		log.debug(utils.method.msg_kw(f"!!!!!!!!!!!!!!!!!!! self._items size: {len(self._items)}"))
		for item_info in self._items:
			item = item_info.item
			assert item is not None

			size_hint = item.sizeHint()
			space_x, space_y = self._calculate_spacing(item)
			w = size_hint.width() + space_x
			log.debug(f"w={w}, x={x}, space_x={space_x}, rect.right()={rect.right()}")
			if item_info.new_row or (x + w > rect.right() and row_height > 0):
				if not test_only:
					self._distribute_space(rect, row_items, rect.right() - x)
				x = rect.x()
				y += row_height + space_y
				row_height = 0
				row_items = []

			if not test_only:
				internals = item.widget() or item.layout()
				internals.setGeometry(QRect(QPoint(x, y), size_hint))

			row_items.append(item)
			x += w
			row_height = max(row_height, size_hint.height())
			log.debug(f"Row height: {row_height}")

		if not test_only:
			self._distribute_space(rect, row_items, rect.right() - x)

		log.debug(utils.method.msg_kw("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"))

		return y + row_height - rect.y()

	def _distribute_space(self, rect, row_items, remaining_space):
		if not row_items:
			return
		space_per_item = remaining_space // len(row_items)
		log.debug("========================")
		log.debug(utils.function.msg_kw(f"Space per item: {space_per_item}"))
		x = 0
		for i, item in enumerate(row_items):
			internals = item.widget() or item.layout()
			geometry = item.geometry()
			size = internals.sizeHint()
			w = size.width() + space_per_item
			size.setWidth(w)
			geometry.setX(x)
			geometry.setSize(size)
			x += w
			assert geometry.width() >= 0
			item.setGeometry(geometry)
			
			log.debug(utils.function.msg_kw(f"Item {i} geometry: {geometry}"))
		log.debug("-======================-")
			# internals.setGeometry(geometry)


	def _calculate_spacing(self, item):
		wid = item.widget()
		spacing = self.spacing()
		if wid is not None:
			style = wid.style()
			space_x = spacing + style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
			space_y = spacing + style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
		elif item.layout() is not None:
			space_x, space_y = spacing, spacing
		else:
			space_x, space_y = 0, 0
		return space_x, space_y