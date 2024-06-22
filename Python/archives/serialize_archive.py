# # It will take the values from the previous frame automatically, but can be provided with a dictionary of values if is called from another level.
# def assign_attrs(self, values=None):
# 	kwargs = values or inspect.currentframe().f_back.f_locals
# 	init_params = inspect_utils.method_parameters(self.__init__)
# 	custom_mapping = self._serialize_mapping()
# 	not_provided_args = []
# 	for param_name, value in init_params.items():
# 		attr_name = custom_mapping.get(param_name) or param_name
# 		if param_name not in kwargs:
# 			not_provided_args.append(param_name)
# 		else:
# 			setattr(self, attr_name, kwargs[param_name])
# 	if not_provided_args:
# 		raise Exception(utils.function.msg(f"Not provided arguments: {not_provided_args}"))
def assign_attrs(self, values=None):
	kwargs = values or {}
	init_params = {}

	# Get the class hierarchy up to Serializable
	class_hierarchy = inspect.getmro(self.__class__)
	class_hierarchy = [cls for cls in class_hierarchy if issubclass(cls, Serializable) and cls != Serializable]

	# Traverse the stack frames
	current_frame = inspect.currentframe().f_back
	while current_frame:
		frame_locals = current_frame.f_locals
		frame_self = frame_locals.get('self', None)

		# Check if the frame belongs to a method call related to this instance
		if isinstance(frame_self, self.__class__) and frame_self is self:
			# Iterate over the class hierarchy to find the matching class
			for cls in class_hierarchy:
				if cls.__init__.__code__ == current_frame.f_code:
					# Collect init params for this class
					cls_init_params = inspect_utils.method_parameters(cls.__init__)
					init_params.update(cls_init_params)
					kwargs.update(frame_locals)
					break
			current_frame = current_frame.f_back
			continue
		break

	# Process the collected parameters
	custom_mapping = self._serialize_mapping()
	not_provided_args = []
	for param_name in init_params:
		attr_name = custom_mapping.get(param_name) or param_name
		if param_name not in kwargs:
			not_provided_args.append(param_name)
		else:
			setattr(self, attr_name, kwargs[param_name])

	if not_provided_args:
		raise Exception(utils.function.msg(f"Not provided arguments: {not_provided_args}"))