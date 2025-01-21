import random
import timeit

# from test import *

name = "Alice"

def fstring_speed_test():
	name = random.choice(["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Kevin", "Linda", "Mallory", "Nancy", "Oscar", "Peggy", "Quentin", "Romeo", "Sybil", "Trent", "Ursula", "Victor", "Walter", "Xander", "Yvonne", "Zelda"])
	print(timeit.timeit('f"Hello, {name}!"', globals=globals(), number=1000000))
	print(timeit.timeit('"Hello, %s!" % name', globals=globals(), number=1000000))

def test():
	log(title("Fstring Speed Test"))
	fstring_speed_test()
	log(title("End of Fstring Speed Test"))

# run()
fstring_speed_test()
