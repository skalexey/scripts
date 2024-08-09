import time


class TimeProfiler:
	def __init__(self, print_function=None):
		self.start_time = None
		self.last_time = None
		self._print_function = print_function or print
		self._marks = []
		self._measurements = []
		super().__init__()
	
	def start(self):
		self._marks.clear()
		self._measurements.clear()
		self.start_time = time.time()
		self.last_time = self.start_time

	def mark(self, description=None):
		last_time, start_time, current_time = self.last_time, self.start_time, time.time()
		if start_time is None:
			start_time = current_time
		if last_time is None:
			last_time = current_time
		self.last_time, self.start_time = current_time, start_time
		mark = self.Measurement(current_time - last_time, description)
		self._marks.append(mark)
		return mark

	def measure(self, description=None):
		measurement = self.Measurement(time.time() - self.start_time, description)
		self._measurements.append(measurement)
		return measurement

	# Measure and print
	def print_measure(self, description=None):
		measured_time = self.measure().timespan
		desc_addition = f" on {description}" if description else ""
		self.print(f"Time elapsed{desc_addition}: {measured_time}")

	def print_marks(self, format=None):
		_format = format or "Mark '{description}': {timespan} sec."
		for mark in self._marks:
			self.print(_format.format(description=mark.description, timespan=mark.timespan))

	def print_measurements(self, format=None):
		_format = format or "Measurementment '{description}': {timespan} sec."
		for measurement in self._measurements:
			self.print(_format.format(description=measurement.description, timespan=measurement.timespan))

	def print_all(self):
		self.print_measurements()
		self.print_marks()

	def print(self, message):
		self._print_function(message)

	def set_print_function(self, print_function):
		self._print_function = print_function


	class Measurement:
		def __init__(self, timespan, description=None):
			self.timespan = timespan
			self.description = description
