import re


def lock_owner(lock):
	repr = lock.__repr__()
	# Find 'owner=<id>' in the repr
	owner = re.search(r'owner=(\d+)', repr)
	if owner is None:
		return None
	return int(owner.group(1))
