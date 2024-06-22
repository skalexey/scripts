# def frame_function(frame):
# 	frame_function_name = frame.f_code.co_name
# 	frame_function = frame.f_globals.get(frame_function_name)
# 	if frame_function is None:
# 		self = frame.f_locals.get('self')
# 		if self is not None:
# 			frame_function = getattr(self, frame_function_name)
# 	if frame_function is None:
# 		raise ValueError(f"Could not find function '{frame_function_name}' in frame '{frame}'")
# 	return frame_function


# def current_function_signature():
# 	frame = inspect.currentframe().f_back
	
# 	# Get the current function name
# 	func_name = frame.f_code.co_name
	
# 	# Get the stack frames to identify the class context
# 	outer_frames = inspect.getouterframes(frame)
	
# 	# Iterate through the stack to find the class and method context
# 	for outer_frame in outer_frames:
# 		frame_info = inspect.getframeinfo(outer_frame.frame)
# 		func_qualname = frame_info.function
# 		if '.' in func_qualname:
# 			class_name = func_qualname.split('.')[0]
			
# 			# Find the class object in the globals or locals
# 			base_class = outer_frame.frame.f_globals.get(class_name, None)
# 			if base_class is None:
# 				base_class = outer_frame.frame.f_locals.get(class_name, None)
			
# 			if base_class is not None and hasattr(base_class, func_name):
# 				func = getattr(base_class, func_name)
# 				if inspect.isfunction(func) or inspect.ismethod(func):
# 					return signature_str(func)
	
# 	raise ValueError("Function could not be found in the base class.")

def frame_class(frame):
	frame_locals = frame.f_locals
	code = frame.f_code
	frame_class = frame_locals.get('__class__', None)
	if frame_class is not None:
		return frame_class
	# Try to get the class object from local and global scope
	frame_class_name = frame_locals.get('__class__', None)
	if frame_class_name is not None:
		return frame_class_name
	frame_globals = frame.f_globals


def frame_function(frame):
	func_name = frame.f_code.co_name
	frame_locals = frame.f_locals
	frame_class = frame_locals.get('__class__', None)
	if frame_class is not None:
		return frame_class.__dict__[func_name]
	# Try to get the function object from local and global scope
	result = frame.f_locals.get(func_name, None) or frame.f_globals.get(func_name, None)
	# # If the function is a method, it might be in an object in the local scope, since methods have self as the first argument, but it can be named differently
	# if result is None:
	# 	frame_self = frame_locals.get('self', None)
	# 	frame_locals_values = frame_locals.values()
	# 	candidates = itertools.chain([frame_self], frame_locals_values) if frame_self else frame_locals_values
	# 	for obj in candidates:
	# 		if hasattr(obj, func_name):
	# 			func = getattr(obj, func_name)
	# 			if inspect.ismethod(func) or inspect.isfunction(func):
	# 				result = func
	# 				break
	if result is None:
		raise ValueError("Function could not be found in the current frame.")
	return result