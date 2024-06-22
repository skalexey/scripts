import collections
import inspect
import json
import os
from datetime import datetime
from enum import Enum

import utils.class_utils as class_utils
import utils.collection_utils as collection_utils
import utils.function
import utils.import_utils as import_utils
import utils.inspect_utils as inspect_utils
import utils.json_utils as json_utils
import utils.lang
import utils.method
import utils.string


class NotSerializable:
	pass

# If you want to serialize to another type, consider providing the value already converted to that type, but the type must be json-serializable.
# For overridings see Serializable.serialize(**kwargs)).
def to_json_struct(obj, default=NotSerializable, throw=True, overwrite=False):
	if json_utils.is_primitive(obj):
		return obj
	if isinstance(obj, Serializable):
		return obj.serialize(serializer=to_json_struct)
	elif isinstance(obj, datetime):
		return str(obj)
	if isinstance(obj, (dict, collections.OrderedDict)):
		return to_dict(obj, to_json_struct, default, throw, overwrite)
	elif isinstance(obj, list):
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
		if isinstance(data, (dict, collections.OrderedDict)):
			return to_dict(data, stringify_json, default, throw, overwrite)
		elif isinstance(data, list):
			return to_list(data, stringify_json, default, throw, overwrite)
	if throw:
		raise Exception(utils.function.msg(f"Not supported type '{type(data)}' encountered"))
	else:
		return default

def to_json(obj, default=NotSerializable, throw=True, overwrite=False, fpath=None):
	data = to_json_struct(obj, default, throw, overwrite)
	return stringify_json(data, default, throw, overwrite, fpath)

def from_json(json_str=None, fpath=None, carry_over_additional_kwargs=False, **additional_kwargs):
	if json_str is None:
		if fpath is None:
			raise Exception(utils.function.msg("No json_str or fpath provided"))
		try:
			with open(fpath, 'r') as f:
				json_str = f.read()
		except Exception as e:
			raise Exception(utils.function.msg(f"Error reading file '{fpath}': {e}"))
	data = json_utils.load(json_str)
	return from_json_struct(data, carry_over_additional_kwargs, **additional_kwargs)

def from_json_struct(data, carry_over_additional_kwargs=False, **additional_kwargs):
	def go_recursion(obj):
		return from_json_struct(obj, carry_over_additional_kwargs, **(additional_kwargs if carry_over_additional_kwargs else {}))
	if json_utils.is_primitive(data):
		if isinstance(data, str):
			if utils.string.is_datetime(data):
				return datetime.fromisoformat(data)
		return data
	elif isinstance(data, list):
		return [go_recursion(item) for item in data]
	elif isinstance(data, (dict, collections.OrderedDict)):
		classname = data.get("classname")
		if classname is None:
			return {key: go_recursion(value) for key, value in data.items()}
		cls = import_utils.find_or_import_class(classname)
		return cls.deserialize(data, deserializer=from_json_struct, carry_over_additional_kwargs=carry_over_additional_kwargs, **additional_kwargs)
	else:
		raise Exception(utils.function.msg(f"Not deserializable object of type '{type(data)}' encountered"))

def kwargs_from_dict(data, deserializer=from_json_struct, carry_over_additional_kwargs=False, **additional_kwargs):
	caller_args = utils.function.args()
	return class_kwargs_from_dict(**caller_args)[1]

def class_kwargs_from_dict(data, deserializer=from_json_struct, carry_over_additional_kwargs=False, **additional_kwargs):
	classname = data.get("classname")
	if classname is None:
		raise Exception(utils.function.msg("No 'classname' value provided in the data"))
	cls = import_utils.find_or_import_class(classname)
	result = inspect_utils.method_parameters(cls.__init__)
	# Fill the result with the values from the data
	for key, val in data.items():
		if key in result:
			if json_utils.is_serializable(val):
				result[key] = deserializer(val, carry_over_additional_kwargs, **(additional_kwargs if carry_over_additional_kwargs else {}))
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
	elif isinstance(data, list):
		obj = [go_recursion(item) for item in data]
	elif isinstance(data, dict):
		obj = {key: go_recursion(value) for key, value in data.items()}
	return obj

def from_db_data(data, carry_over_additional_kwargs=False, **additional_kwargs):
	obj = json_obj_from_db_data(data, carry_over_additional_kwargs, **additional_kwargs)
	return from_json_struct(obj, carry_over_additional_kwargs, **additional_kwargs)

class Serializable:
	def __init__(self, assign_attrs=True, *args, **kwargs):
		if assign_attrs:
			init_args = utils.method.chain_args(Serializable)
			self.assign_all_attrs(init_args)
		super().__init__(*args, **kwargs)

	def _serialize_mapping(self):
		return {}

	def serialize(self, ignore=None, serializer=to_json_struct, allow_overrides=False, **param_overrides):
		init_params = inspect_utils.method_parameters(self.__init__)
		for param_name in collection_utils.as_set(ignore):
			init_params.pop(param_name, None)
		# Process overridings
		custom_mapping = self._serialize_mapping()
		collection_utils.fill_dict(init_params, self.__dict__, ignore=custom_mapping)
		for param_name, attr_name in custom_mapping.items():
			if param_name in init_params:
				init_params[param_name] = self.__dict__[attr_name]
		if "classname" in init_params:
			raise Exception(utils.function.msg(f"'classname' is a reserved name for serialization and cannot be used as a parameter name"))
		classname = class_utils.class_path(self.__class__)
		init_params.insert(0, "classname", classname)
		if not allow_overrides:
			not_supported_params = [key for key in param_overrides if key not in init_params]
			if not_supported_params:
				raise Exception(utils.function.msg(f"Not supported parameters provided through kwargs: {not_supported_params}"))
		init_params.update(param_overrides)
		# Avoid infinite recursion for serializable collections by converting them to OrderedDict
		_init_parms = collections.OrderedDict(init_params) if isinstance(init_params, Serializable) else init_params
		serialized = serializer(_init_parms, overwrite=False)
		return serialized
	
	# def collect_init_args(self):
	# It will take the values from the previous frame automatically, but can be provided with a dictionary of values if is called from another level.
	def assign_all_attrs(self, values):
		init_params = utils.method.chain_params(self.__init__, Serializable)
		# Process the collected parameters
		custom_mapping = self._serialize_mapping()
		# Every argument except ignored must be provided for a Serializable
		not_provided_args = []
		for param_name in init_params:
			attr_name = custom_mapping.get(param_name) or param_name
			if param_name not in values:
				not_provided_args.append(param_name)
			else:
				setattr(self, attr_name, values[param_name])

		if not_provided_args:
			raise Exception(utils.function.msg(f"Not provided arguments: {not_provided_args}"))
	
	@classmethod
	# carry_over_additional_kwargs:
	#  If True, all the additional_kwargs will be propagated to all objects to be deserialized, but only those from the receiver object parameter list will be used.
	#  If False, an exception will be thrown if additional_kwargs contains keys that are not parameters of __init__ method of the class of object to be deserialized.
	def deserialize(cls, data, deserializer=from_json_struct, carry_over_additional_kwargs=False, **additional_kwargs):
		cls, kwargs = class_kwargs_from_dict(data, deserializer, carry_over_additional_kwargs, **additional_kwargs)
		return cls(**kwargs)

	def deserialize_into_self(self, data, deserializer=from_json_struct, carry_over_additional_kwargs=False, **additional_kwargs):
		caller_args = utils.method.args()
		kwargs = kwargs_from_dict(**caller_args)
		self.assign_all_attrs(kwargs)
		

class DBSerializable(Serializable):
	def serialize(self, ignore=None, **kwargs):
		return super().serialize(ignore=ignore, serializer=to_db_data, **kwargs)

	@classmethod
	def deserialize(cls, data, deserializer=from_db_data, carry_over_additional_kwargs=False, **additional_kwargs):
		return super().deserialize(**caller_args)
