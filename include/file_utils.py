import re
import sys
import collections.abc

def insert_before(fpath, where, what):
	return replace(fpath, where, what + where, 1)

def replace(fpath, where, what, count = -1):
	with open(fpath, "r") as f:
		contents = f.read()
	pos = contents.find(where)
	if (pos < 0):
		print(-1)
		return -1
	
	contents = contents.replace(where, what, count)

	with open(fpath, "w") as f:
		f.write(contents)

	print(pos)
	return pos

def convert(fpath, current, target):
	try:
		with open(fpath, "rb") as f:
			contents = f.read().decode(current)
			f.close()
			with open(fpath, "wb") as f:
				print("Convert ", fpath, " from ", current, " to ", target)
				converted = contents.encode(target)
				f.write(converted)
		return 0
	except FileNotFoundError:
		return -1

def search(fpath, what, count = 1):
	if (type(count) != int):
		count = 1
	with open(fpath, "r", encoding="utf-8") as f:
		contents = f.read()
	# whatUTF8 = what.encode(encoding = 'UTF-8', errors = 'strict').decode('utf-8')
	# print("whatUTF8: ", whatUTF8)
	# print("what: ", what)
	contents = re.sub(r"\r", " ", contents)
	contents = re.sub(r"\n", " ", contents)
	res = re.findall(what, contents)
	# print("len(res): ",len(res))
	for p in res:
		if (isinstance(p, collections.abc.Sequence)):
			p = p[len(p) - 3]
		print(p.encode("utf-8"))
		return p
	return -1

def find(fpath, what, count = 1):
	if (type(count) != int):
		count = 1
	with open(fpath, "r", encoding="utf-8") as f:
		contents = f.read()
	# whatUTF8 = what.encode(encoding = 'UTF-8', errors = 'strict').decode('utf-8')
	# print("whatUTF8: ", whatUTF8)
	print("what: ", what)
	match=(re.search(what, contents))
	print("res: ",match.start())
	
	return res

if len(sys.argv) > 2:
	arr = []
	for i, a in enumerate(sys.argv):
		if (i > 1):
  			arr.append(a)
	locals()[sys.argv[1]](*arr)
elif len(sys.argv) == 2:
	locals()[sys.argv[1]]()
