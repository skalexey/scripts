import sys

class A:
	def a(self):
		print("A.a")

class B:
	def b(self):
		print("B.b")

class C(A, B):
	def a(self):
		super().a()
		print("C.a")

def test():
	c = C()
	c.a()

function_name = sys.argv[1] if len(sys.argv) > 1 else "test"
locals()[function_name]()
