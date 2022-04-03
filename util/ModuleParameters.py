
class ModuleParameters:
	"""Helper functions for parameters"""

	def get_parameter(self, parameter_name: str):
		return self.parameters[parameter_name]
	
	def save_parameter(self, parameter_name: str, value, **options):
		"""saves parameter. switch type if applicable"""

		# **options:
		#   param_type: float, int. If empty, assume the type is string.

		param_type = options.get('param_type', "str")
		if param_type == "float":
			value = float(value)
		elif param_type == "int":
			value = int(value)
		self.parameters[parameter_name]
		return

	def save_parameters_list(self,
							 parameter_names: list,
							 values: list,
							 **options):
		assert len(parameter_names) == len(values), \
			"Number of parameters must be the same as the number of assigned values"
		for param_index in range(len(parameter_names)):
			self.save_parameter(parameter_names[param_index], values[param_index])
		return