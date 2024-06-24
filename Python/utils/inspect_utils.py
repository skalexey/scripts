import inspect
import itertools

import utils


def is_value_empty(value):
	return value == inspect.Parameter.empty

def function_parameters(func, out=None):
	return signature_input(func, out, lambda param: param.kind is not inspect.Parameter.VAR_KEYWORD and param.kind is not inspect.Parameter.VAR_POSITIONAL)

def signature_input(func, out=None, filter=None):
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

def method_parameters(method, out=None):
	params = function_parameters(method, out)
	assert len(params) > 0, f"Method '{method.__name__}' has no self or cls parameter"
	params.remove_at(0)
	return params

def current_function_signature(custom_frame=None):
	frame = custom_frame or caller_frame()
	func = frame_function(frame)
	return signature_str(func)

def signature_str(func):
	if hasattr(func, '__self__'):
		class_name = func.__self__.__class__.__name__
	elif hasattr(func, '__qualname__'):
		class_name = func.__qualname__.split('.')[0]
	else:
		class_name = None
	class_name_addition = f"{class_name}." if class_name is not None else ""
	return f"{class_name_addition}{func.__name__}{inspect.signature(func)}"

def frame_function(frame):
	call_info = frame_call_info(frame)
	return call_info.function
	
class CallInfo:
	def __init__(self, frame):
		self.frame = frame
		self.co_name = None
		self.function = None
		self.caller = None
		self.cls = None
		self.method = None

		co_name = frame.f_code.co_name
		self.co_name = co_name
		if co_name == "<module>":
			return
		previous_frame = frame.f_back
		# Try to get the function object from local scope on the level above
		func = previous_frame.f_locals.get(co_name)
		if func is None:
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

def caller_frame(level=-2):
	return relframe(level)

# Find the frame where the provided object is used
def user_frame(obj=None):
	return user_frame_info(obj).frame

def user_frame_info(obj=None):
	frame_info = None
	stack = inspect.stack()
	if obj is None:
		_caller_frame = caller_frame()
		caller_module = _caller_frame.f_globals.get('__name__', None)
	for frame_info in stack[1:]:
		# Check if the class if not Logger
		frame = frame_info.frame
		frame_locals = frame.f_locals
		if obj is not None:
			frame_self = frame_locals.get('self', None)
			# If it is a call of a local funciton, or another class method, then we found it
			if frame_self is None or not isinstance(frame_self, obj.__class__):
				break
		else:
			# Find the first frame out of this module
			if caller_module is None:
				break
			if frame.f_globals.get('__name__', None) != caller_module:
				break
	if frame_info is None:
		raise ValueError(f"Could not find the frame of where the provided object is used (obj: {obj})")
	return frame_info

