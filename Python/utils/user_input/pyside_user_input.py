import threading

import utils.pyside
from utils.context import *


def input(message):
	event = threading.Event()
	answer = None
	def on_answer(value):
		nonlocal answer
		answer = value
		event.set()
	def job_for_main_thread():
		utils.pyside.show_input_dialog("Input", message, on_answer)
	GlobalContext.app.do_in_main_thread(job_for_main_thread)
	event.wait()
	return answer

def message(title, message):
	print(f"{title}: {message}")
	# Wait for any key press
	input("Press any key to continue...")

def ask_input(message, on_answer):
	while True:
		answer = input(f"{message}: ")
		on_answer_result = on_answer(answer)
		if on_answer_result is True:
			break
		elif on_answer_result is False:
			print("Invalid input.")
		else:
			print(on_answer_result)

def ask_yes_no(message, on_answer):
	while True:
		answer = input(f"{message} (y/n): ")
		# lowercase the answer
		answer = answer.lower()
		if answer == "y" or answer == "yes":
			on_answer(True)
		elif answer == "n" or answer == "no":
			on_answer(False)
		else:
			print("Invalid input.")
			continue
		break
	