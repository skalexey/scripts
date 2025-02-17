def clamp(value, _min, _max):
	return max(_min, min(value, _max))

# direction 1 for up, -1 for down
def triangle_vertices(origin, size, direction, cls):
	return [cls(origin.x, origin.y - size * direction), cls(origin.x - size, origin.y + size * direction), cls(origin.x + size, origin.y + size * direction)]

def triangle_vertices_point(origin, size, direction, cls):
	double_size_direction = size * 2 * direction
	return [cls(origin.x, origin.y), cls(origin.x - size, origin.y + double_size_direction), cls(origin.x + size, origin.y + double_size_direction)]
