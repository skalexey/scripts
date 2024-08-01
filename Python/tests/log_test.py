from test import *


def log_test():
	def delivery_test():
		log(title("Delivery Test"))
		for i in range(100):
			log(f"Log message {i}")
			sleep(0.5)
		log(title("End of Delivery Test"))

	delivery_test()

def test():
	log(title("Log Test"))
	log_test()
	log(title("End of Log Test"))

run()
