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
	