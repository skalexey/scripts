
def insert_before(fpath, where, what):
	with open(fpath, "r") as f:
		contents = f.read()
	pos = contents.find(where)
	if (pos < 0):
		print("-1")
		return 1
	
	contents = contents.replace(where, what + where, 1)

	with open(fpath, "w") as f:
		f.write(contents)

	print(pos)

