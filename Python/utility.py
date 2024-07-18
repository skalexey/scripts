def filter_list(list, pred):
	return [x for x in list if pred(x)]

def skip_none(cb, val, *args, **kwargs):
	return cb(val, *args, **kwargs) if val is not None else None
