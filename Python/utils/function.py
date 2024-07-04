import inspect

import utils.inspect_utils as inspect_utils


def params(func, out=None, filter=None):
	var_positional_name = None
	keep_var_positional = False
	def sig_filter(param, filter=filter):
		if param.kind is inspect.Parameter.VAR_POSITIONAL:
			nonlocal var_positional_name
			var_positional_name = param.name
		else:
			if var_positional_name is not None:
				if param.kind is not inspect.Parameter.VAR_KEYWORD:
					nonlocal keep_var_positional
					keep_var_positional = True # Keep *args if it goes before declared keyword parameters
			if param.kind is inspect.Parameter.VAR_KEYWORD:
				return False
		if filter is not None:
			if not filter(param):
				return False
		return True
	result = inspect_utils.signature_input(func, out, sig_filter)
	if not keep_var_positional:
		result.pop(var_positional_name, None)
	return result

def args(out=None, validate=True, custom_frame=None, extract_args=None, extract_kwargs=None):
	_frame = custom_frame or inspect_utils.caller_frame()
	_extract_kwargs = extract_kwargs or False
	_extract_args = extract_args or False
	func = inspect_utils.frame_function(_frame)
	_locals = _frame.f_locals
	result = inspect_utils.signature_input(func, out)
	keyword_vars = {}
	positional_vars = []
	missed_args = []
	for key, value in result.items():
		arg = _locals.get(key, inspect.Parameter.empty)
		if arg is inspect.Parameter.empty:
			if validate:
				missed_args.append(key)
			continue
		if value is inspect.Parameter.VAR_KEYWORD:
			if _extract_kwargs:
				keyword_vars[key] = arg
				continue
		if value is inspect.Parameter.VAR_POSITIONAL:
			if _extract_args:
				positional_vars.append(arg)
				continue
		result[key] = arg
	for key, var in keyword_vars.items():
		result.pop(key)
		# Mix in the other kwargs not defined in the function signature
		for k, v in var.items():
			if k in result:
				# This case should never happen, so this check is only for integrity
				raise ValueError(msg(f"Unexpected error: Duplicated argument passed through kwargs: '{k}'"))	
			result[k] = v
	# TODO: move on a higher level
	for var in positional_vars:
		raise ValueError(msg(f"Unexpected error: Positional arguments are not supported: '{var}'"))
	if validate:
		# Check for missing arguments
		if missed_args:
			raise ValueError(msg(f"Missed arguments while carrying over: {missed_args}"))
	return result

def msg(message=None, args_format=None, frame=None, ignore_first=None):
	_args_format = args_format or False
	sig_str = inspect_utils.current_function_signature(custom_frame=frame or inspect_utils.caller_frame(), args_format=_args_format, ignore_first=ignore_first)
	message_addition = f": {message}" if message is not None else ""
	return f"{sig_str}{message_addition}"

def msg_kw(message=None, frame=None):
	return msg(message, args_format="kw", frame=frame or inspect_utils.caller_frame())

def msg_v(message=None, frame=None):
	return msg(message, args_format="values", frame=frame or inspect_utils.caller_frame())
