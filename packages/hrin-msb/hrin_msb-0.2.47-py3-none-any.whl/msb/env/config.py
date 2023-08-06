import os

from .constants import (NameConst)


# Env variable class
class EnvVar(object):
	_key = None

	_value = None

	def __init__(self, key: str = '', value: str = ''):
		self._key = key
		self._value = value

	def __str__(self):
		return f"{self._key} : {self._value}"

	def as_str(self, default: str = '') -> str:
		return default if self._value is None else self._value

	def as_int(self, default: int = 0) -> int:
		return default if self._value is None else int(self._value)

	def as_float(self, default: float = 0.0) -> float:
		return default if self._value is None else float(self._value)

	def as_bool(self, default: bool = False) -> bool:
		if self._value is not None:
			return (int(self._value) > 0) if self._value.isnumeric() \
				else self._value.lower() in ['yes', 'true', '1']
		else:
			return default

	def as_list(self, sep='|', default: list = None) -> list:
		default = default if default is not None else []
		return default if self._value is None else self._value.split(sep=sep)

	def as_tuple(self, sep='|', default: tuple = None) -> tuple:
		default = default if default is not None else tuple()
		return tuple(self.as_list(sep=sep, default=list(default)))

	def as_dict(self, sep='|', kv_sep: str = '=', default: dict = None) -> dict:
		default = default if default is not None else dict()
		lst = self.as_list(sep=sep)
		if len(lst) > 0:
			return {
				str(item).strip().split(kv_sep)[0]:
					str(item).strip().split(kv_sep)[1]
				for item in lst}

	def as_path(self, default='', joinpath: str = None):
		if joinpath is not None:
			return os.path.join(joinpath, self.as_str(default=default))
		return self.as_str(default=default)


class Config:

	@staticmethod
	def load(env_path: str = '', main_file: str = '', local_file: str = ''):
		from .core import load_config
		load_config(env_path, main_file, local_file)

	@staticmethod
	def is_loaded() -> bool:
		return os.environ.get(NameConst.ENV_LOAD_STATUS_KEY_NAME) is not None

	@staticmethod
	def get(key: str = '', default=None) -> EnvVar:
		return EnvVar(key=key, value=os.environ.get(key, default=default))

	@staticmethod
	def get_settings(name: str, default=None):
		from django.conf import settings
		return getattr(settings, name, default)

	@staticmethod
	def debug():
		return Config.get(NameConst.DEBUG_VARIABLE_NAME).as_bool(default=False)

	@staticmethod
	def env_name() -> str | None:
		return Config.get(NameConst.ENVIRONMENT_VARIABLE_NAME).as_str(default=None)

	@staticmethod
	def is_local_env():
		return Config.env_name() == 'local'

	@staticmethod
	def is_dev_or_test_env() -> bool:
		return str(Config.env_name()).lower() in NameConst.DEV_OR_TEST_ENV_NAMES_LIST
