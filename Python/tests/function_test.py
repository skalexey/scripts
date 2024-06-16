cnt = 0
def f():
	global cnt
	cnt += 1
	return cnt

while (a := f()) < 10:
	pass
print(a)