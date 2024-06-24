import collections
import json
import os
from datetime import datetime
from enum import Enum

import utils.collection_utils as collection_utils
import utils.function
import utils.import_utils as import_utils
import utils.inspect_utils as inspect_utils
import utils.json_utils as json_utils
import utils.lang
import utils.method
import utils.serialize
import utils.string


class NotSerializable:
	pass

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

def stringify_json(obj, default=NotSerializable, throw=True, overwrite=False, fpath=None):
	if json_utils.is_serializable(obj):
		if json_utils.is_primitive(obj):
			return obj
		if fpath:
			try:
				from utils.log.logger import Logger
				log = Logger()
				log.info(f"Storing json to '{fpath}'")
				if not os.path.exists(os.path.dirname(fpath)):
					dirpath = os.path.dirname(fpath)
					log.info(f"Creating storage directory '{dirpath}'")
					os.makedirs(dirpath)
				with open(fpath, 'w') as f:
					json.dump(obj, f, indent='\t')
				log.success(f"Stored successfully to '{fpath}'")
				return True
			except Exception as e:
				if throw:
					raise Exception(utils.function.msg(f"Error writing to file '{fpath}': {e}"))
				else:
					return default
		return json.dumps(obj, indent='\t')
	if throw:
		raise Exception(utils.function.msg(f"Not supported type '{type(obj)}' encountered"))
	else:
		return default
	
def to_db_data(obj, default=NotSerializable, throw=True, overwrite=False):
	data = to_json_struct(obj, default, throw, overwrite)
	if json_utils.is_serializable(data):
		if json_utils.is_primitive(data):
			return data
		if json_utils.is_dictionary(data):
			return to_dict(data, stringify_json, default, throw, overwrite)
		elif json_utils.is_list(data):
			return to_list(data, stringify_json, default, throw, overwrite)
	if throw:
		raise Exception(utils.function.msg(f"Not supported type '{type(data)}' encountered"))
	else:
		return default

def to_json(obj, default=NotSerializable, throw=True, overwrite=False, fpath=None):
	data = to_json_struct(obj, default, throw, overwrite)
	return stringify_json(data, default, throw, overwrite, fpath)

def from_json(json_str=None, fpath=None, carry_over_additional_kwargs=False, parse_result_processor=None, **additional_kwargs):
	if json_str is None:
		if fpath is None:
			raise Exception(utils.function.msg("No json_str or fpath provided"))
		try:
			with open(fpath, 'r') as f:
				json_str = f.read()
		except Exception as e:
			raise Exception(utils.function.msg(f"Error reading file '{fpath}': {e}"))
	data = json_utils.load(json_str)
	if parse_result_processor:
		data = parse_result_processor(data)
	if not json_utils.is_serializable(data):
		return data # Return processor result
	return from_json_struct(data, carry_over_additional_kwargs, **additional_kwargs)

def from_json_struct(data, carry_over_additional_kwargs=False, **additional_kwargs):
	def go_recursion(obj):
		return from_json_struct(obj, carry_over_additional_kwargs, **(additional_kwargs if carry_over_additional_kwargs else {}))
	if json_utils.is_primitive(data):
		if isinstance(data, str):
			if utils.string.is_datetime(data):
				return datetime.fromisoformat(data)
		return data
	elif json_utils.is_list(data):
		return [go_recursion(item) for item in data]
	elif json_utils.is_dictionary(data):
		classpath = data.get("classpath")
		if classpath is None:
			return {key: go_recursion(value) for key, value in data.items()}
		cls = import_utils.find_or_import_class(classpath)
		return cls.deserialize(data, deserializer=from_json_struct, carry_over_additional_kwargs=carry_over_additional_kwargs, **additional_kwargs)
	else:
		raise Exception(utils.function.msg(f"Not deserializable object of type '{type(data)}' encountered"))

def kwargs_from_dict(data, deserializer=from_json_struct, carry_over_additional_kwargs=False, **additional_kwargs):
	caller_args = utils.function.args()
	return class_kwargs_from_dict(**caller_args)[1]

def class_kwargs_from_dict(data, deserializer=None, carry_over_additional_kwargs=False, **additional_kwargs):
	_deserializer = deserializer or from_json_struct
	classpath = data.get("classpath")
	if classpath is None:
		raise Exception(utils.function.msg("No 'classpath' value provided in the data"))
	cls = import_utils.find_or_import_class(classpath)
	result = inspect_utils.method_parameters(cls.__init__)
	# Fill the result with the values from the data
	for key, val in data.items():
		if key in result:
			if json_utils.is_serializable(val):
				result[key] = _deserializer(val, carry_over_additional_kwargs, **(additional_kwargs if carry_over_additional_kwargs else {}))
			else:
				raise Exception(utils.function.msg(f"Not deserializable object of type '{type(val)}' encountered"))
	# Fill the result with the additional_kwargs
	if not carry_over_additional_kwargs:
		not_supported_params = [key for key in additional_kwargs if key not in result]
		if not_supported_params:
			sig_str = inspect_utils.signature_str(cls.__init__)
			raise Exception(f"Not supported parameters provided for {sig_str} through kwargs: {not_supported_params}")
	collection_utils.update_existing(result, additional_kwargs)
	# Check for missed required parameters
	not_provided_params = [key for key, val in result.items() if inspect_utils.is_value_empty(val) and key not in result]
	if not_provided_params:
		sig_str = inspect_utils.signature_str(cls.__init__)
		raise Exception(f"Missing values for a required parameters: {not_provided_params} for {sig_str}")
	return cls, result

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
	return from_json_struct(obj, carry_over_additional_kwargs, **additional_kwargs)


