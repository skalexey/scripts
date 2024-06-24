import collections

import utils.class_utils as class_utils
import utils.collection_utils as collection_utils
import utils.function
import utils.serialize as serialize
from utils.object.attributes_view import *


class Serializable:
	def __init__(self, assign_attrs=True, *args, **kwargs):
		if assign_attrs:
			init_args = utils.method.chain_args(Serializable)
			self.assign_all_attrs(init_args)
		super().__init__(*args, **kwargs)

	def _serialize_mapping(self):
		# __init__(self, p1, p2=v2) parameters named as <key> from this list will be stored to self.<value> if the value is not None
		return {}

	def serialize(self, ignore=None, serializer=None, allow_extension=False, **param_overrides):
		_serializer = serializer or serialize.to_json_struct
		init_params = utils.method.chain_params(self.__init__, Serializable)
		for param_name in collection_utils.as_set(ignore):
			init_params.pop(param_name, None)
		# Process overridings
		custom_mapping = self._serialize_mapping()
		attrs = AttributesView(self)
		collection_utils.fill_dict(init_params, attrs, ignore=custom_mapping)
		for param_name, attr_name in custom_mapping.items():
			if param_name in init_params:
				if attr_name is not None:
					init_params[param_name] = attrs[attr_name]
		if "classpath" in init_params:
			raise Exception(utils.function.msg(f"'classpath' is a reserved name for serialization and cannot be used as a parameter name"))
		classpath = class_utils.class_path(self.__class__)
		init_params.insert(0, "classpath", classpath)
		if not allow_extension:
			not_supported_params = [key for key in param_overrides if key not in init_params]
			if not_supported_params:
				raise Exception(utils.function.msg(f"Not supported parameters provided through kwargs: {not_supported_params}"))
		init_params.update(param_overrides)
		# Avoid infinite recursion for serializable collections by converting them to OrderedDict
		_init_parms = collections.OrderedDict(init_params) if isinstance(init_params, Serializable) else init_params
		serialized = _serializer(_init_parms, overwrite=False)
		return serialized
	
	# def collect_init_args(self):
	# It will take the values from the previous frame automatically, but can be provided with a dictionary of values if is called from another level.
	def assign_all_attrs(self, values):
		init_params = utils.method.chain_params(self.__init__, Serializable)
		# Process the collected parameters
		custom_mapping = self._serialize_mapping()
		# Every argument except ignored must be provided for a Serializable
		not_provided_args = []
		for param_name in init_params.keys():
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
	def deserialize(cls, data, deserializer=None, carry_over_additional_kwargs=False, **additional_kwargs):
		caller_args = utils.method.args()
		cls, kwargs = serialize.class_kwargs_from_dict(**caller_args)
		return cls(**kwargs)

	def deserialize_into_self(self, data, deserializer=None, carry_over_additional_kwargs=False, **additional_kwargs):
		caller_args = utils.method.args()
		kwargs = serialize.kwargs_from_dict(**caller_args)
		self.assign_all_attrs(kwargs)
		

class DBSerializable(Serializable):
	def serialize(self, ignore=None, **kwargs):
		return super().serialize(ignore=ignore, serializer=serialize.to_db_data, **kwargs)

	@classmethod
	def deserialize(cls, data, deserializer=None, carry_over_additional_kwargs=False, **additional_kwargs):
		caller_args = utils.method.args()
		return super().deserialize(**caller_args)