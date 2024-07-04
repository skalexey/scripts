import inspect

import utils.function
import utils.inspect_utils as inspect_utils
from utils.collection.ordered_dict import OrderedDict


def args(out=None, validate=True, custom_frame=None, extract_kwargs=None):
	result = utils.function.args(out, validate, custom_frame=(custom_frame or inspect_utils.caller_frame()), extract_kwargs=extract_kwargs)
	assert len(result) > 0, f"Method has no self or cls parameter"
	result.remove_at(0)
	return result

def is_first_arg_valid(arg):
	# Check if it's a class method (arg is a class)
	if inspect.isclass(arg):
		return True
	# Check if it's an instance method (arg is an instance of a class)
	if hasattr(arg, '__class__') and not inspect.isclass(arg):
		return True
	return False

def params(method_or_func, out=None, filter=None):
	func = inspect_utils.function(method_or_func)
	_params = utils.function.params(func, out, filter=filter)
	if len(_params) <= 0:
		raise Exception(f"Method '{func.__name__}' has no self or cls parameter")
	if not is_first_arg_valid(_params.value_at(0)):
		raise ValueError(utils.function.msg(f"First parameter of method '{func.__name__}' must be a class or an instance of a class"))
	_params.remove_at(0)
	return _params

def filter_params(all_attrs, method):
	_params = params(method)
	attrs = all_attrs.__class__()
	kwargs = all_attrs.__class__()
	for key, val in all_attrs.items():
		where = kwargs if key in _params else attrs
		where[key] = val
	return kwargs, attrs

# Goes through the MRO and collects all the parameters of the method implementations in its class hierarchy
# mro_end - the class to stop the search at
def chain_params(method_or_func, cls=None, mro_end=None, out=None, filter=None):
	if inspect.isfunction(method_or_func):
		if cls is None:
			raise ValueError(utils.function.msg("Class must be provided for a function"))
		func = method_or_func
		_cls = cls
	elif inspect.ismethod(method_or_func):
		func = method_or_func.__func__
		_cls = method_or_func.__self__.__class__
	else:
		raise ValueError(utils.function.msg("This function is only used for methods or functions"))
	class_hierarchy = inspect.getmro(_cls)
	if mro_end:
		class_hierarchy = [c for c in class_hierarchy if issubclass(c, mro_end) and c != mro_end]
	result = out or OrderedDict()
	for c in class_hierarchy:
		cls_method = c.__dict__.get(func.__name__)
		if cls_method is not None:
			cls_params = params(cls_method, filter=filter)
			result.update(cls_params)
	return result

# Goes through the stack frames and collects the arguments passed to all the implementations of the same method in the caller class hierarchy up to the base_class
def chain_args(base_class=None, out=None, validate=True, custom_frame=None):
	result = out or OrderedDict()
	if validate:
		_params = {}
	caller_frame = custom_frame or inspect_utils.caller_frame()
	call_info = inspect_utils.frame_call_info(caller_frame)
	caller_frame_func = call_info.function
	if not call_info.is_method():
		raise ValueError(utils.function.msg("This function is only used for methods"))
	caller_func_name = caller_frame_func.__name__
	# Get the class hierarchy up to Serializable
	class_hierarchy = inspect.getmro(inspect_utils.cls(call_info.caller))
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
				cls_init_params = params(frame_func)
				if validate:
					_params.update(cls_init_params)
				# Collect the args
				frame_locals = frame.f_locals
				for key, value in cls_init_params.items():
					if key in frame_locals:
						result[key] = frame_locals[key]
						assert result[key] is not inspect.Parameter.empty, f"Parameter '{key}' is empty"
		frame = frame.f_back
		frame_call_info = inspect_utils.frame_call_info(frame) if frame else None

	if validate:
		# Check for missing arguments
		missing_args = []
		for key in _params:
			if key not in result:
				missing_args.append(key)
			elif result[key] is inspect.Parameter.empty:
				missing_args.append(key)
		if missing_args:
			raise ValueError(utils.function.msg(f"Missed arguments: {missing_args}"))

	return result

def msg(message=None, args_format=None, frame=None):
	return utils.function.msg(message, args_format=args_format, frame=frame or inspect_utils.caller_frame(), ignore_first=True)

def msg_kw(message=None, frame=None):
	return msg(message, args_format="kw", frame=frame or inspect_utils.caller_frame())

def msg_v(message=None, frame=None):
	return msg(message, args_format="values", frame=frame or inspect_utils.caller_frame())
