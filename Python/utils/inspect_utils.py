import inspect
import itertools

import utils  # Lazy import
import utils.function


def is_value_empty(value):
	return value == inspect.Parameter.empty

def signature_input(func, out=None, filter=None):
	if func is None:
		raise ValueError(utils.function.msg("The given argument is not a method or a function"))
	signature = inspect.signature(func)
	result = out or utils.ordered_dict.OrderedDict()
	for param in signature.parameters.values():
		if filter is not None:
			if not filter(param):
				continue
		if param.kind is inspect.Parameter.VAR_KEYWORD or param.kind is inspect.Parameter.VAR_POSITIONAL:
			result[param.name] = param.kind
		else:
			result[param.name] = param.default
	return result

def current_function_signature(custom_frame=None, noargs=False):
	frame = custom_frame or caller_frame()
	call_info = frame_call_info(frame)
	func = call_info.function
	if func is None:
		return f"{call_info.co_name}()"
	return signature_str(func, noargs=noargs)

def signature_str(func, noargs=False):
	if hasattr(func, '__self__'):
		class_name = func.__self__.__class__.__name__
	elif hasattr(func, '__qualname__'):
		class_name = func.__qualname__.rsplit('.', 1)[0]
	else:
		class_name = None
	class_name_addition = f"{class_name}." if class_name is not None else ""
	args_sig = inspect.signature(func) if not noargs else "()"
	return f"{class_name_addition}{func.__name__}{args_sig}"

def frame_function(frame):
	call_info = frame_call_info(frame)
	return call_info.function

def module_name(frame=None):
	frame = frame or caller_frame()
	return frame.f_globals.get('__name__', None)

class CallInfo:
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
		func = previous_frame.f_locals.get(co_name)
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
		candidates = itertools.chain([frame_self], frame_locals_values) if frame_self else frame_locals_values
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
							if cls_func.__code__ == frame.f_code: # Function and class determined
								self.function = cls_func
								self.cls = cls
								self.caller = obj
								# An instance has only one method per name, so this call may not be of the method
								if method_func.__code__ == frame.f_code:
									self.method = method_func
									return
					if self.function is not None:
						return
			raise ValueError(f"Couldn't retrieve call information for the code object '{co_name}'")

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

# Properties can have getter and setter function bound to the same name
def functions(obj):
	result = []
	if inspect.isfunction(obj):
		result.append(obj)
	if inspect.ismethod(obj):
		result.append(obj.__func__)
	if hasattr(obj, '__func__'):
		result.append(obj.__func__)
	if isinstance(obj, property):
		attrs = ['fget', 'fset']
		for name in attrs:
			func = getattr(obj, name)
			if func is not None:
				result.append(func)
	return result

# For methods and functions returns the function bound to the object, for properties returns the getter
def function(obj):
	funcs = functions(obj)
	return funcs[0] if funcs else None

def cls(obj):
	if inspect.isclass(obj):
		return obj
	if inspect.isfunction(obj):
		return None
	if inspect.ismethod(obj):
		return cls(obj.__self__)
	if hasattr(obj, '__class__'):
		return obj.__class__
	return None
	
def call_info():
	frame = caller_frame()
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

