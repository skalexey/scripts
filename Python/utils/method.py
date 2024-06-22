import inspect

import utils.function
import utils.inspect_utils as inspect_utils


def args(out=None, validate=True, custom_frame=None):
	result = utils.function.args(out, validate, custom_frame=(custom_frame or inspect_utils.caller_frame()))
	result.pop('self', None)
	return result

# Goes through the MRO and collects all the parameters of the method implementations in its class hierarchy
def chain_params(method, base_class=None, out=None):
	class_hierarchy = inspect.getmro(inspect_utils.cls(method))
	if base_class:
		class_hierarchy = [cls for cls in class_hierarchy if issubclass(cls, base_class) and cls != base_class]
	result = out or {}
	for cls in class_hierarchy:
		cls_method = cls.__dict__.get(method.__name__)
		if cls_method is not None:
			cls_params = inspect_utils.method_parameters(cls_method)
			result.update(cls_params)
	return result

# Goes through the stack frames and collects the arguments passed to all the implementations of the same method in the caller class hierarchy up to the base_class
def chain_args(base_class=None, out=None, validate=True, custom_frame=None):
	result = out or {}
	if validate:
		params = {}
	caller_frame = custom_frame or inspect_utils.caller_frame()
	call_info = inspect_utils.frame_call_info(caller_frame)
	caller_frame_func = call_info.function
	if not call_info.is_method():
		raise ValueError(utils.function.msg("This function is only used for methods"))
	caller_func_name = caller_frame_func.__name__
	# Get the class hierarchy up to Serializable
	class_hierarchy = inspect.getmro(call_info.caller.__class__)
	if base_class:
		class_hierarchy = [cls for cls in class_hierarchy if issubclass(cls, base_class) and cls != base_class]

	frame_call_info = call_info
	# Traverse the stack frames
	while frame_call_info:
		frame = frame_call_info.frame
		frame_self = frame_call_info.caller
		# Check if the frame belongs to a method call related to this instance
		if frame_self is not call_info.caller:
			break
		# Iterate over the class hierarchy to find the matching class
		frame_cls = frame_call_info.cls
		if frame_cls in class_hierarchy:
			frame_func = frame_call_info.function
			func_name = frame_func.__name__
			if func_name == caller_func_name:
				# Collect params for this class call of frame_func
				cls_init_params = inspect_utils.method_parameters(frame_func)
				if validate:
					params.update(cls_init_params)
				# Collect the args
				frame_locals = frame.f_locals
				for key, value in cls_init_params.items():
					if key in frame_locals:
						result[key] = frame_locals[key]
		frame = frame.f_back
		frame_call_info = inspect_utils.frame_call_info(frame) if frame else None

	if validate:
		# Check for missing arguments
		missing_args = []
		for key in params:
			if key not in result:
				missing_args.append(key)
		if missing_args:
			raise ValueError(utils.function.msg(f"Missed arguments: {missing_args}"))

	return result