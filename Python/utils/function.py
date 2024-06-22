import inspect

import utils.collection_utils as collection_utils
import utils.function
import utils.inspect_utils as inspect_utils


def args(out=None, validate=True, custom_frame=None):
	_frame = custom_frame or inspect_utils.caller_frame()
	func = inspect_utils.frame_function(_frame)
	_locals = _frame.f_locals
	result = inspect_utils.signature_input(func, out)
	keyword_vars = {}
	positional_vars = []
	missing_args = []
	for key, value in result.items():
		arg = _locals.get(key, None)
		if arg is None:
			if validate:
				missing_args.append(key)
			continue
		if value is inspect.Parameter.VAR_KEYWORD:
			keyword_vars[key] = arg
			continue
		if value is inspect.Parameter.VAR_POSITIONAL:
			positional_vars.append(arg)
			continue
		result[key] = arg
	for key, var in keyword_vars.items():
		result.pop(key)
		# Mix in the other kwargs not defined in the function signature
		for k, v in var.items():
			if k in result:
				# This case should never happen, so this check is only for integrity
				raise ValueError(utils.function.msg(f"Unexpected error: Duplicated argument passed through kwargs: '{k}'"))	
			result[k] = v
	for var in positional_vars:
		raise ValueError(utils.function.msg(f"Unexpected error: Positional arguments are not supported: '{var}'"))
	if validate:
		# Check for missing arguments
		if missing_args:
			raise ValueError(utils.function.msg(f"Missed arguments while carrying over: {missing_args}"))
	return result

def msg(msg):
	sig_str = inspect_utils.current_function_signature(custom_frame=inspect_utils.caller_frame())
	return f"{sig_str}: {msg}"