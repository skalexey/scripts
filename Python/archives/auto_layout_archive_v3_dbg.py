class ItemInfo:
	def __init__(self, item, new_row=False):
		self.item = item
		self.new_row = new_row
		self.rect = QRect()
		self.spacing = QSize(0, 0)

	@property
	def internals(self):
		return self.item.widget() or self.item.layout()

	def __repr__(self):
		return f"{self.__class__.__name__}(item={self.internals}, rect={self.rect}, spacing={self.spacing}, new_row={self.new_row})"

	def update_render_info(self):
		self.rect = QRect()
		self.spacing = QSize(0, 0)
		size = self._calculate_size()
		self.rect.setSize(size)
		self.spacing = self._calculate_spacing()
		assert self.rect.height() == size.height()
		assert self.rect.x() >= 0
		assert self.rect.y() >= 0
		# internals = self.item.widget() or self.item.layout()
		# internals_size = internals.sizeHint()
		# assert size_hint.height() == internals_size.height()

	@property
	def size(self):
		return self.rect.size()

	def _calculate_spacing(self):
		wid = self.item.widget()
		if wid is not None:
			style = wid.style()
			space_x = max(0, style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)) # TODO: check if this clamp is needed
			space_y = max(0, style.layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)) # TODO: check if this clamp is needed
		else:
			space_x, space_y = 0, 0
		return QSize(space_x, space_y)

	def _calculate_size(self):
		widget = self.item.widget()
		size = QSize()
		if widget:
			size = widget.sizeHint()
		else:
			layout = self.item.layout()
			if layout:
				for i in range(self.item.layout().count()):
					nested_item = self.item.layout().itemAt(i)
					size = nested_item.sizeHint().expandedTo(size)
				size_hint = layout.sizeHint()
				assert QSize_ge(size_hint, size) # Layouts expand to fit all the space available, but can not be smaller than the sum of their children
		return size

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
		layout_info = self._do_layout(QRect(0, 0, width, 0))
		return layout_info.rect.height()

	def setGeometry(self, rect):
		log.debug(utils.method.msg_kw())
		super().setGeometry(rect)
		layout_info = self._do_layout(rect)
		layout_info.distribute_space()


	class RowInfo:
		def __init__(self, spacing=None):
			self.rect = QRect()
			self.spacing = spacing or int()
			self.items = []

		def __bool__(self):
			return bool(self.items)
		
		def spacing_x_to(self, item_info):
			last_item_spacing = self.items[-1].spacing.width() if self.items else 0
			spacing = max(item_info.spacing.width(), last_item_spacing)
			return spacing

		def add_item(self, item_info):
			spacing_x = self.spacing_x_to(item_info)
			row_size = self.rect.size()
			target = self.rect.topLeft() + QPoint(row_size.width() + spacing_x, 0)
			item_info.rect.moveTo(target)
			self.items.append(item_info)
			self.rect = self.rect.united(item_info.rect)
			self.spacing = max(item_info.spacing.height(), self.spacing)
			
		def translate(self, dx, dy):
			self.rect.translate(dx, dy)
			for item_info in self.items:
				item_info.rect.translate(dx, dy)

		@property
		def size(self):
			return self.rect.size()
		

	class LayoutInfo:
		def __init__(self, items, rect=None, spacing=None):
			log.debug(utils.function.msg(f"======= Start ======= rect={rect}, spacing={spacing}"))
			self.rect = rect or QRect()
			self.rows = []
			self.spacing = spacing or QSize(0, 0)
			for i, item_info in enumerate(items):
				item = item_info.item
				assert item is not None
				geometry_before = item_info.rect
				self.add_item(item_info)
				assert item_info.rect.top() == self.rows[-1].rect.top()
				log.debug(utils.function.msg(f"Item {i}: {item_info}"))
			log.debug(utils.function.msg("======= End ======="))

		def add_item(self, item_info):
			item_info.update_render_info()
			row = self.rows[-1] if self.rows else None
			if not row or item_info.new_row or (row.size.width() + row.spacing_x_to(item_info) + item_info.size.width()) > self.rect.width():
				row = self._new_row()
			spacing_before = row.spacing
			row.add_item(item_info)
			self._validate()
			if len(row.items) > 1:
				spacing_diff = row.spacing - spacing_before
				if spacing_diff > 0:
					row.translate(0, spacing_diff)
			self.rect = self.rect.united(row.rect)
			self._validate()

		def _validate(self):
			for i, row in enumerate(self.rows):
				for g, item_info in enumerate(row.items):
					assert item_info.rect.x() >= 0
					assert item_info.rect.y() >= 0
		
		def distribute_space(self):
			if not self.rows:
				return
			for row in self.rows:
				remaining_space = self.rect.width() - row.size.width()
				space_per_item = remaining_space // len(row.items)
				log.debug("========================")
				log.debug(utils.method.msg_kw(f"Space per item: {space_per_item}, layout rect: {self.rect}, row rect: {row.rect}"))
				x = 0
				for i, item_info in enumerate(row.items):
					item = item_info.item
					internals = item.widget() or item.layout()
					geometry = item_info.rect
					# log.debug(utils.method.msg_kw(f"Item {i} geometry before: {geometry}"))
					internals_size = internals.sizeHint()
					size = geometry.size()
					assert size.height() >= internals_size.height()
					w = size.width() + space_per_item
					size.setWidth(w)
					geometry.setX(x)
					geometry.setSize(size)
					x += w
					assert geometry.width() >= 0
					assert item_info.rect == geometry
					item.setGeometry(geometry)
					# log.debug(utils.method.msg_kw(f"Added space for {item_info}: {space_per_item}"))
				log.debug("-======================-")

		def _new_row(self):
			last_row = self.rows[-1] if self.rows else None
			spacing = max(last_row.spacing, self.spacing.height()) if last_row else self.spacing.height()
			row = AutoLayout.RowInfo(spacing=spacing)
			if last_row:
				row.rect.moveTo(last_row.rect.bottomLeft())
				row.rect.translate(0, last_row.spacing)
			else:
				row.rect.moveTo(self.rect.topLeft())
			self.rows.append(row)
			return row


	def _do_layout(self, rect):
		spacing = self.spacing()
		layout_info = self.LayoutInfo(self._items, rect=QRect(rect.topLeft(), QSize(rect.width(), rect.height())), spacing=QSize(spacing, spacing)) # Copy the rect
		return layout_info