if __name__ == '__main__':
	from tests.test import *

	def is_open_test():
		log(title("Start of Is File Opened For Writing Test"))

		def opened_file_test():
			log(title("Opened File Test"))
			fpath = 'example.txt'
			log(f"Writting to file '{os.path.abspath(fpath)}'")
			with open(fpath, "a+") as f:
				f.write("Writing to a file")
				assert is_open(fpath), f"The file '{fpath}' should be opened for writing."
			assert not is_open(fpath), f"The file '{fpath}' should be closed"
			log.success("End of Opened File Test")

		def not_existing_file_test():
			log(title("Not Existing File Test"))
			fpath = 'not_existing_file.txt'
			assert not is_open(fpath), f"The file '{fpath}' should not exist nor opened"
			log.success("End of Not Existing File Test")

		opened_file_test()
		not_existing_file_test()

		log.success(title("End of Is File Opened For Writing Test"))

	def test():
		is_open_test()

	run()