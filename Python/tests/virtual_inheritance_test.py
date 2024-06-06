import sys

def test1():
	print("Test 1")
	class A:
		def __init__(self, i):
			self.i = i
			pass

	class B(A):
		def __init__(self, i):
			super().__init__(i)
			pass

	class C(A):
		def __init__(self, i):
			super().__init__(i)
			pass

	class D(B, C):
		def __init__(self, i):
			super().__init__(i)
			pass

	d = D(1)
	print(d.i)
	print("End of test 1")

def test2():
	print("Test 2")
	class A:
		def __init__(self, i):
			self.i = i

		def print_i(self):
			print(self.i)

	class B(A):
		def __init__(self, i):
			super().__init__(i)

		def b_print_i(self):
			self.print_i()

	class C(A):
		def __init__(self, i, j):
			super().__init__(i)
			self.j = j

		def c_print_i(self):
			self.print_i()

		def c_print_j(self):
			print(self.j)

	class D(B, C):
		# TypeError: test2.<locals>.B.__init__() takes 2 positional arguments but 3 were given
		# def __init__(self, i, j):
		# 	super().__init__(i, j)

		def __init__(self, i, j):
			B.__init__(self, i)
			C.__init__(self, i, j)

		def d_print_i(self):
			print(self.i)

		def d_print_j(self):
			print(self.j)

	d = D(1, 2)
	d.b_print_i()
	d.c_print_i()
	d.c_print_j()
	d.d_print_i()
	d.d_print_j()
	print("End of test 2")

def test3():
	print("Test 3")
	
	class A:
		def __init__(self, i, *args, **kwargs):
			print("A init")
			# super().__init__(*args, **kwargs)
			self.i = i

		def print_i(self):
			print(self.i)

	class B(A):
		def __init__(self, i, b, *args, **kwargs):
			print("B init")
			super().__init__(i, *args, **kwargs)
			self.b = b

		def b_print_i(self):
			self.print_i()

		def b_print_b(self):
			print(self.b)

	class C(A):
		def __init__(self, i, c, *args, **kwargs):
			print("C init")
			super().__init__(i, *args, **kwargs)
			self.c = c

		def c_print_i(self):
			self.print_i()

		def c_print_c(self):
			print(self.c)

	class D(B, C):
		def __init__(self, i, b, c, d):
			print("D init")
			super().__init__(i, b, c, d)
			# B.__init__(self, i, b, c, d)
			# C.__init__(self, i, b, c, d)
			self.d = d

		def d_print_i(self):
			print(self.i)

		def d_print_c(self):
			print(self.c)

		def d_print_d(self):
			print(self.d)

	d = D(1, 2, 3, 4)
	d.b_print_i()
	d.b_print_b()
	d.c_print_i()
	d.c_print_c()
	d.d_print_i()
	d.d_print_c()
	d.d_print_d()
	print("End of test 3")


def test():
	test1()
	test2()

function_name = sys.argv[1] if len(sys.argv) > 1 else "test"
locals()[function_name]()
