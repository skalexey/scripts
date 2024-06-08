from abc import ABC, abstractmethod


def title(string, filler='=', length=80):
	# Generate a line of the given length with string in the middle separated by spaces from the filler on the sides
	# Example: title("Hello", "=", 80) -> "================================== Hello =================================="
	# Example: title("Hello", "-", 80) -> "---------------------------------- Hello ---------------------------------"
	# Example: title("Hello", "=", 20) -> "======== Hello ========"
	left_length = (length - len(string) - 2) // 2
	right_length = length - len(string) - 2 - left_length
	return f"{filler * left_length} {string} {filler * right_length}"

class AbstractTextSpinner(ABC):
	def __init__(self):
		self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
		self.frame_index = 0
		self.frame_period = 0.1
		self._time_since_last_frame = 0

	@property
	def frame_index(self):
		return self._frame_index

	@frame_index.setter
	def frame_index(self, value):
		self._frame_index = value
		self.text = self.frames[self.frame_index]

	def reset(self):
		self.frame_index = 0

	def update(self, dt):
		self._time_since_last_frame += dt
		if self._time_since_last_frame >= self.frame_period:
			self.update_frame()
		

	@property
	def text(self):
		return None

	def update_frame(self):
		self.frame_index = (self.frame_index + 1) % len(self.frames)
		self._time_since_last_frame -= self.frame_period

class TextSpinner(AbstractTextSpinner):
	def __init__(self):
		self._text = None
		super().__init__()

	@AbstractTextSpinner.text.getter
	def text(self):
		return self._text
	
	@AbstractTextSpinner.text.setter
	def text(self, value):
		self._text = value
