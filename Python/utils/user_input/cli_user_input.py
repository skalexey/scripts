import sys


def input(message):
	# Make a console input
	# Read the input and return it
	print(message)
	return sys.stdin.readline().strip()

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
	

# Tests
def test_input():
	assert input("Enter 'hello': ") == "hello"
	
	def on_answer_world(answer):
		assert answer == "world"
		return True

	ask_input("Enter 'world'", on_answer_world)

	def on_yes_no_answer_yes(answer):
		assert answer == True

	ask_yes_no("Enter 'y'", on_yes_no_answer_yes)

	def on_yes_no_answer_no(answer):
		assert answer == False

	ask_yes_no("Enter 'n'", on_yes_no_answer_no)


if __name__ == "__main__":
	test_input()
	print("utils/user_input/pyside_user_input.py is OK")