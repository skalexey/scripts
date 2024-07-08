import collections
import inspect
import json
import os
from datetime import datetime
from enum import Enum

import utils.collection
import utils.function
import utils.import_utils as import_utils
import utils.inspect_utils as inspect_utils
import utils.json_utils as json_utils
import utils.lang
import utils.method
import utils.serialize  # Lazy import
import utils.string
from utils.collection.ordered_set import OrderedSet
from utils.log.logger import Logger

log = Logger()

class NotSerializable:
	def __bool__(self):
		return False

# If you want to serialize to another type, consider providing the value already converted to that type, but the type must be json-serializable.
# For overridings see Serializable.serialize(**kwargs)).
def to_json_struct(obj, default=NotSerializable, throw=True, overwrite=False):
	if json_utils.is_primitive(obj):
		return obj
	if isinstance(obj, utils.serialize.Serializable):
		return obj.serialize(serializer=to_json_struct)
	elif isinstance(obj, datetime):
		return str(obj)
	if json_utils.is_dictionary(obj):
		return to_dict(obj, to_json_struct, default, throw, overwrite)
	elif json_utils.is_list(obj):
		return to_list(obj, to_json_struct, default, throw, overwrite)
	elif isinstance(obj, Enum):
		return obj.name # Name by default.
	if throw:
		raise Exception(utils.function.msg(f"Type '{type(obj)}' is not serializable"))
	return default

def to_dict(obj, serializer, default=NotSerializable, throw=True, overwrite=False):
	result = obj if overwrite else ({} if isinstance(obj, dict) else collections.OrderedDict())
	iter = obj.items()
	def exception_msg(not_serializable_elements):
		return f"Fields '{not_serializable_elements}' are not serializable"
	return to_collection(result, serializer, default, throw, overwrite, iter, exception_msg)

def to_list(obj, serializer, default=NotSerializable, throw=True, overwrite=False):
	result = obj if overwrite else [None] * len(obj)
	iter = enumerate(obj)
	def exception_msg(not_serializable_elements):
		return f"Elements '{not_serializable_elements.values()}' are not serializable"
	return to_collection(result, serializer, default, throw, overwrite, iter, exception_msg)		

def to_collection(result, serializer, default=NotSerializable, throw=True, overwrite=False, iter=None, gen_exception_msg=None):
	not_serializable_elements = {} # key/index -> type/class
	for key, val in iter:
		out = serializer(val, default, throw, overwrite)
		if out is NotSerializable:
			not_serializable_elements[key] = type(val)
		result[key] = out
	
	if not_serializable_elements:
		if throw:
			msg = gen_exception_msg(not_serializable_elements)
			raise Exception(utils.function.msg(msg))
		else:
			return default
	return result

def to_db_data(obj, default=NotSerializable, throw=True, overwrite=False):
	data = to_json_struct(obj, default, throw, overwrite)
	if json_utils.is_serializable(data):
		if json_utils.is_primitive(data):
			return data
		if json_utils.is_dictionary(data):
			return to_dict(data, json_utils.stringify, default, throw, overwrite)
		elif json_utils.is_list(data):
			return to_list(data, json_utils.stringify, default, throw, overwrite)
	if throw:
		raise Exception(utils.function.msg(f"Not supported type '{type(data)}' encountered"))
	else:
		return default

def to_json(obj, default=NotSerializable, throw=True, overwrite=False, fpath=None):
	data = to_json_struct(obj, default, throw, overwrite)
	return json_utils.stringify(data, default, throw, overwrite, fpath)

def from_json(json_str=None, fpath=None, carry_over_additional_kwargs=False, parse_result_processor=None, **additional_kwargs):
	if json_str is None:
		if fpath is None:
			raise Exception(utils.function.msg("No json_str or fpath provided"))
		try:
			with open(fpath, 'r') as f:
				json_str = f.read()
		except FileNotFoundError:
			log.warning(utils.function.msg_kw(f"File '{fpath}' not found"))
			return None
		except Exception as e:
			raise Exception(utils.function.msg(f"Error reading file '{fpath}': {e}"))
	data = json_utils.load(json_str)
	if parse_result_processor:
		data = parse_result_processor(data)
	if not json_utils.is_serializable(data):
		return data # Return processor result
	return from_json_struct(data, carry_over_additional_kwargs, True, **additional_kwargs)

def from_json_struct(data, carry_over_additional_kwargs=False, overwrite=False, **additional_kwargs):
	def go_recursion(obj):
		return from_json_struct(obj, carry_over_additional_kwargs, overwrite, **(additional_kwargs if carry_over_additional_kwargs else {}))
	if json_utils.is_primitive(data):
		if isinstance(data, str):
			if utils.string.is_datetime(data):
				return datetime.fromisoformat(data)
		return data
	elif json_utils.is_list(data):
		result = data if overwrite else [None] * len(data)
		for i, item in enumerate(data):
			result[i] = go_recursion(item)
		return result
	elif json_utils.is_dictionary(data):
		classpath = data.get("classpath")
		if classpath is None:
			result = data if overwrite else {}
			for key, value in data.items():
				result[key] = go_recursion(value)
			return result
		cls = import_utils.find_or_import_class(classpath)
		return cls.deserialize(data, deserializer=from_json_struct, carry_over_additional_kwargs=carry_over_additional_kwargs, overwrite=overwrite, **additional_kwargs)
	else:
		raise Exception(utils.function.msg(f"Not deserializable object of type '{type(data)}' encountered"))

def attrs_from_dict(data, deserializer=from_json_struct, carry_over_additional_kwargs=False, overwrite=False, **additional_kwargs):
	caller_frame = inspect_utils.caller_frame()
	return class_attrs_from_dict(data, deserializer=from_json_struct, carry_over_additional_kwargs=False, overwrite=False, caller_frame=caller_frame, **additional_kwargs)[1:4]

def class_attrs_from_dict(data, deserializer=None, carry_over_additional_kwargs=False, overwrite=False, caller_frame=None, **additional_kwargs):
	_deserializer = deserializer or from_json_struct
	classpath = data.get("classpath")
	if classpath is None:
		raise Exception(utils.function.msg("No 'classpath' value provided in the data"))
	cls = import_utils.find_or_import_class(classpath)
	all_attrs = collect_all_params(cls)
	_caller_frame = caller_frame or inspect_utils.caller_frame()
	args = utils.method.chain_args(utils.serialize.Serializable, custom_frame=_caller_frame)
	call_info = inspect_utils.frame_call_info(_caller_frame)
	base_params = utils.method.params(getattr(utils.serialize.Serializable, call_info.co_name))
	args -= base_params
	if len(args) > 0:
		print("args", args)
	all_attrs.update(args)
	# Distribute
	not_supported_params = OrderedSet()
	for key, val in data.items():
		if key in all_attrs:
			if json_utils.is_serializable(val):
				all_attrs[key] = _deserializer(val, carry_over_additional_kwargs, overwrite, **(additional_kwargs if carry_over_additional_kwargs else {}))
				assert all_attrs[key] is not NotSerializable
				assert all_attrs[key] is not inspect.Parameter.empty
			else:
				raise Exception(utils.function.msg(f"Not deserializable object of type '{type(val)}' encountered"))
		else:
			not_supported_params.add(key)
	not_supported_params.pop("classpath")
	# Check for not supported parameters
	if not_supported_params:
		sig_str = inspect_utils.signature_str(cls.__init__, cls)
		raise Exception(f"Not supported parameters provided for {sig_str} in data: {not_supported_params}")
	if not carry_over_additional_kwargs:
		not_supported_additional_kwargs = additional_kwargs.keys() - all_attrs.keys()
		not_supported_params.update(not_supported_additional_kwargs)
		if not_supported_params:
			sig_str = inspect_utils.signature_str(cls.__init__, cls)
			raise Exception(f"Not supported parameters provided for {sig_str} through kwargs: {not_supported_params}")
	# Apply additional kwargs atop
	utils.collection.update_existing(all_attrs, additional_kwargs)
	kwargs, attrs = utils.method.filter_params(all_attrs, cls.__init__)
	# Check for missed required parameters
	not_provided_params = [key for key, val in kwargs.items() if inspect_utils.is_value_empty(val)]
	if not_provided_params:
		sig_str = inspect_utils.signature_str(cls.__init__, cls)
		raise Exception(f"Missing values for a required parameters: {not_provided_params} for {sig_str}")
	return cls, all_attrs, kwargs, attrs

def json_obj_from_db_data(data, carry_over_additional_kwargs=False, **additional_kwargs):
	def go_recursion(obj):
		return json_obj_from_db_data(obj, carry_over_additional_kwargs, **(additional_kwargs if carry_over_additional_kwargs else {}))

	obj = data
	if isinstance(data, str):
		struct = json_utils.load(data)
		if struct is not None:
			obj = struct
	elif json_utils.is_list(data):
		obj = [go_recursion(item) for item in data]
	elif json_utils.is_dictionary(data):
		obj = {key: go_recursion(value) for key, value in data.items()}
	return obj

def from_db_data(data, carry_over_additional_kwargs=False, **additional_kwargs):
	obj = json_obj_from_db_data(data, carry_over_additional_kwargs, **additional_kwargs)
	return from_json_struct(obj, carry_over_additional_kwargs, True, **additional_kwargs)

def collect_all_params(cls):
	def filter(param):
		return param.kind is not inspect.Parameter.VAR_POSITIONAL
	return utils.method.chain_params(cls.__init__, cls, mro_end=utils.serialize.Serializable, filter=filter)
