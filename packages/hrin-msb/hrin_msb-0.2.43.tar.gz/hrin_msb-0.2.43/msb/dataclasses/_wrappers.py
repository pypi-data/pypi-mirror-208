class ConfigObject(object):
	_config_key_name = "key"
	_config_value_name = "value"

	def __typcasted_value(self, key, val):
		try:
			return key.__class__(val)
		except Exception:
			return val

	def __parse_config_key_value(self, config_obj):
		_key = getattr(config_obj, self._config_key_name) if hasattr(config_obj, self._config_key_name) else None
		_value = getattr(config_obj, self._config_value_name) if hasattr(config_obj, self._config_value_name) else None
		return _key, _value

	def __init__(self, *config_list):
		for config in config_list:
			config_key, config_value = self.__parse_config_key_value(config_obj=config)
			if hasattr(self, config_key) and config_value is not None:
				setattr(self, config_key, config_value)
