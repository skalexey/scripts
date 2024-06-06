def f(variable_dict):
	variable_dict['value'] = "something"

class Test:
	def __init__(self):
		self.v1 = 1
		self.v2 = 2
		self.condition = True

	def run(self):
		variable_dict = {'value': None}
		if self.condition:
			variable_dict['value'] = self.v1
		else:
			variable_dict['value'] = self.v2
		print(f"Values before modification: v1: {self.v1}, v2: {self.v2}")
		f(variable_dict)
		print(f"Values after modification: v1: {self.v1}, v2: {self.v2}")

Test().run()
