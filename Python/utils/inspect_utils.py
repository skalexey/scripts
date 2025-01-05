import inspect
import itertools

import utils  # Lazy import for less important modules
import utils.function


def is_value_empty(value):
	return value == inspect.Parameter.empty

def signature_input(func, out=None, filter=None):
	"""
	Returns a dictionary with parameters of a function with their default values, or VAR_KEYWORD/VAR_POSITIONAL for variadic aliases (*args and **kwargs).
	Optionally filters out some of them based on the given predicate.
	"""
	if func is None:
		raise ValueError(utils.function.msg("The given argument is not a method or a function"))
	signature = inspect.signature(func)
	result = out or utils.collection.ordered_dict.OrderedDict()
	for param in signature.parameters.values():
		if filter is not None:
			if not filter(param):
				continue
		if param.kind is inspect.Parameter.VAR_KEYWORD or param.kind is inspect.Parameter.VAR_POSITIONAL:
			result[param.name] = param.kind
		else:
			result[param.name] = param.default
	return result

def current_function_signature(custom_frame=None, args_format=None, ignore_first=None):
	"""
	Constructs a string with the signature of the current function.
	"""
	frame = custom_frame or caller_frame()
	call_info = frame_call_info(frame)
	func = call_info.function
	if func is None:
		return f"{call_info.co_name}()"
	return signature_str(func, call_info.cls, frame, args_format=args_format, ignore_first=ignore_first)

def signature_str(func, cls=None, frame=None, args_format=None, ignore_first=None):
	"""
	Returns a string representation of a given function's signature.
	"""
	_func = inspect.unwrap(func)
	_frame = frame or caller_frame()
	_args_format = "names" if args_format is None else args_format
	_cls = cls or _get_class(_func)
	class_name = _cls.__name__ if _cls is not None else None
	_ignore_first = 1 if ignore_first or (class_name and ignore_first is None) else 0
	class_name_addition = f"{class_name}." if class_name is not None else ""
	if not _args_format:
		args_sig = "()"
	else:
		sig = inspect.signature(_func)
		if _args_format == "names":
			params = utils.function.params(_func)
			names = list(params.keys())[_ignore_first:]
			args_sig = f"({', '.join(name for name in names)})"
		else:
			call_info = frame_call_info(_frame)
			unwrapped_call_info_function = inspect.unwrap(call_info.function)
			if unwrapped_call_info_function != _func:
				raise ValueError(f"Function mismatch. Provided: '{_func}', what frame contains: '{unwrapped_call_info_function}'")
			all_args = utils.function.args(out=None, validate=False, custom_frame=_frame)
			args = all_args[_ignore_first:]
			if _args_format == "values":
				args_repr = ''
				for i, (name, arg) in enumerate(args.items()):
					param = sig.parameters[name]
					if param.kind is inspect.Parameter.VAR_KEYWORD or param.kind is inspect.Parameter.VAR_POSITIONAL:
						if arg == {} or arg == [] or arg == tuple(): # Scip empty args and kwargs for values format
							continue
					args_repr += f"{', ' if i > 0 else ''}{name}={arg!r}"
				args_sig = f"({args_repr})"
			elif _args_format == "kw":
				kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in args.items())
				args_sig = f"({kwargs_repr})"
			else:
				raise ValueError(f"Unexpected value for args: {args_format}")
	return f"{class_name_addition}{_func.__name__}{args_sig}"

def frame_function(frame):
	"""
	Returns a function of the given frame.
	"""
	call_info = frame_call_info(frame)
	return call_info.function

def module_name(frame=None):
	"""
	Gets the module name where the frame is called.
	"""
	frame = frame or caller_frame()
	return frame.f_globals.get('__name__', None)


class CallInfo:
	"""
	Extended information about the callstack frame with attached module_name, frame, co_name, and:
		* caller object, class, and method in the case of class method call and module name,
		* function in the case of a function call.
	"""

	def __init__(self, frame):
		self.frame = frame
		self.co_name = None
		self.function = None
		self.caller = None
		self.cls = None
		self.method = None
		self.module_name = None

		co_name = frame.f_code.co_name
		self.co_name = co_name
		if co_name == "<module>":
			return
		self.module_name = module_name(frame)
		previous_frame = frame.f_back
		# Try to get the function object from local scope on the level above
		func = previous_frame.f_locals.get(co_name) if previous_frame is not None else None
		if not inspect.isfunction(func):
			# Check the globals of the current frame
			func = frame.f_globals.get(co_name, None)
		if inspect.isfunction(func):
			self.function = func
			return
		# If it is not a function, then try to find the owner of the method
		frame_locals = frame.f_locals
		frame_locals_values = frame_locals.values()
		frame_self = frame_locals.get('self', None)
		candidates = itertools.chain([frame_self], frame_locals_values) if frame_self is not None else frame_locals_values
		for obj in candidates:
			attr = inspect.getattr_static(obj, co_name, None)
			if attr is None:
				continue
			method_funcs = functions(attr)
			for method_func in method_funcs:
				if method_func is not None: # Just for checking if it is a method or a function
					mro = inspect.getmro(obj if inspect.isclass(obj) else obj.__class__)
					for cls in mro:
						cls_method = cls.__dict__.get(co_name, None) # Method or function
						cls_func = function(cls_method) # Function
						if cls_func is not None:
							unwrapped_function = inspect.unwrap(cls_func)
							for f in [cls_func, unwrapped_function]:
								if f.__code__ == frame.f_code: # Function and class determined
									self.function = f
									self.cls = cls
									self.caller = obj
									# An instance has only one method per name, so this call may not be of the method
									if method_func.__code__ == frame.f_code:
										self.method = method_func
										return
									break
					if self.function is not None:
						return
			# raise ValueError(f"Couldn't retrieve call information for the code object '{co_name}'")
			return

	def is_function(self):
		return self.function is not None and self.cls is None
	
	def is_method(self):
		return self.cls is not None
	
	def is_module(self):
		return self.co_name == "<module>"

	def is_classmethod(self):
		return inspect.isclass(self.caller) and isinstance(self.method, classmethod)
	
	def classname(self):
		return self.cls.__name__
	
	def caller_type(self):
		return "class" if inspect.isclass(self.caller) else "object"
	
	def is_caller_class(self):
		return inspect.isclass(self.caller)

	def caller_classname(self):
		return self.caller.__name__ if self.is_caller_class() else self.caller.__class__.__name__

	def __repr__(self):
		if self.is_module():
			return f"CallInfo({self.co_name})"
		return f"CallInfo({self.caller_classname()} {self.caller_type()}->{self.cls.__name__}.{self.function.__name__}())"

def functions(obj):
	"""
	Returns a list of functions that represents the given object. It retrieves getter and setter functions for properties, the function for methods, and the function itself for functions.
	"""
	result = []
	if isinstance(obj, property):
		for name in ['fget', 'fset']:
			func = getattr(obj, name)
			if func is not None:
				assert inspect.isfunction(func)
				result.append(func)
	else:
		func = function(obj)
		if func is not None:
			result.append(func)
	return result

def function(obj):
	"""
	Retrieves the function associated with the given object. It returns function of a method, getter function of a property, and function itself for a function.
	To get both getter and setter use functions(obj)
	"""
	if inspect.isfunction(obj):
		func = obj
	elif inspect.ismethod(obj):
		func = obj.__func__
	else:
		func = getattr(obj, '__func__', None)
		if func is None:
			if isinstance(obj, property):
				func = obj.fget
				if func is not None:
					assert inspect.isfunction(func)
	# Don't unwrap
	return func

def cls(obj):
	"""
	Retrieves the class of an object.
	"""
	if inspect.isclass(obj):
		return obj
	if inspect.isfunction(obj):
		return None
	if inspect.ismethod(obj):
		return cls(obj.__self__)
	return getattr(obj, '__class__', None)

_get_class = cls

def call_info(level=None):
	_level = (level or 0) - 1
	frame = caller_frame(_level)
	return frame_call_info(frame)
	
def frame_call_info(frame):
	return CallInfo(frame)

def relframe(level):
	frame = inspect.currentframe()
	cur = level - 1 # Take into account the current frame
	step = 1 if cur < 0 else -1
	while cur != 0:
		frame = frame.f_back if cur < 0 else frame.f_forward
		cur += step
	return frame

def caller_frame(level=None):
	return relframe((level or 0) - 2) # Excluding relframe and caller_frame calls since we need to go a level above the function where caller_frame is called.

# Find the frame where the provided object is used
def user_frame(obj=None, caller_level=None):
	return user_frame_info(obj, (caller_level or 0) - 1).frame

# Terms:
# User - the user of the object if provided or of the caller module.
# Caller - who called user_frame_info.
# Params:
# obj - the object to find the first frame where it is used going back from this one. If not provided, then the first frame of the user of the caller module is returned.
# caller_level - the level of the caller of user_frame_info.
def user_frame_info(obj=None, caller_level=None):
	frame_info = None
	stack = inspect.stack()
	frame = stack[1].frame
	if obj is None:
		frame = caller_frame(caller_level)
		caller_module = module_name(frame)
	entered_caller_stack = False
	for frame_info in stack[1:]:
		# Check if the class if not Logger
		frame = frame_info.frame
		if obj is not None:
			call_info = frame_call_info(frame)
			if call_info.caller == obj:
				entered_caller_stack = True
			else:
				if entered_caller_stack:
					break
		else:
			# Find the first frame out of this module
			if caller_module is None:
				break
			frame_module = module_name(frame)
			if frame_module == caller_module:
				entered_caller_stack = True
			else:
				if entered_caller_stack:
					if frame_module != caller_module:
						break
	if frame_info is None:
		raise ValueError(f"Could not find the frame of where the provided object is used (obj: {obj})")
	return frame_info

def user_globals_locals(obj=None, globals=None, locals=None):
	if globals is None or locals is None:
		frame = user_frame(obj, -1)
		_globals = frame.f_globals if globals is None else globals
		_locals = frame.f_locals if locals is None else locals
		return _globals, _locals
	return globals, locals