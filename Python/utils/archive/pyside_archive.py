def ask_yes_no(title, message, on_answer=None, yes_text=None, no_text=None):	
	# Simplified version, but without customization:
	# result = QMessageBox.question(None, title, message)
	# if result == QMessageBox.Yes:
	# 	on_yes()
	# else:
	# 	on_no()

def show_message(title, message):
	log.info(f"Show message: {title}, {message}")
	# msg_box = QMessageBox()
	# msg_box.setIcon(QMessageBox.Information)
	# msg_box.setWindowTitle(title)
	# msg_box.setText(message)
	# msg_box.setStandardButtons(QMessageBox.Ok)

	# future = concurrent.futures.Future()
	# def _on_confirm():
	# 	future.set_result(True)
	# 	if on_confirm is not None:
	# 		on_confirm()
	# msg_box.buttonClicked.connect(lambda: _on_confirm())
	# msg_box.exec_()
	# return future
	return QMessageBox.information(None, title, message)
