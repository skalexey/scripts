
def insert_before(fpath, where, what):
	replace(fpath, where, where + what, 1)

def replace(fpath, where, what, count = -1):
	with open(fpath, "r") as f:
		contents = f.read()
	pos = contents.find(where)
	if (pos < 0):
		print("-1")
		return 1
	
	contents = contents.replace(where, what, count)

	with open(fpath, "w") as f:
		f.write(contents)

	print(pos)