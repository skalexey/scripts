class MyClass:
	@classmethod
	def class_method(cls):
		print("Class method called")

MyClass.class_method()  # Works: Output: Class method called
instance = MyClass()
instance.class_method()  # Works: Output: Class method called
