def clamp(value, _min, _max):
	return max(_min, min(value, _max))

# direction 1 for up, -1 for down
def triangle_vertices(origin, size, direction, cls):
	return [cls(origin.x, origin.y - size * direction), cls(origin.x - size, origin.y + size * direction), cls(origin.x + size, origin.y + size * direction)]
