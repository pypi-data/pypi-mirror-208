import logging
import os
from pathlib import Path

from .constants import NameConst
from .exceptions import MsbConfigException


def __get_config_file_type(config_file):
	return os.path.basename(config_file)


def __get_environment_file(config_path: str, main_file: str, local_file: str):
	if not os.path.isdir(config_path):
		raise MsbConfigException.BaseDirDoesNotExists(config_path, desc=config_path)

	local_config_file = Path(config_path).joinpath(local_file)
	main_config_file = Path(config_path).joinpath(main_file)

	if local_config_file.exists():
		return local_config_file.__str__()
	elif main_config_file.exists():
		return main_config_file.__str__()
	else:
		raise MsbConfigException.ConfigFileDoesNotExist(local_config_file, main_config_file)


def __load_configuration_file(config_file: str):
	if NameConst.DOT_ENV_FILE_NAME in config_file:
		from dotenv import load_dotenv
		return load_dotenv(config_file, verbose=True)


def load_config(env_path: str = '', main_file: str = '', local_file: str = ''):
	try:
		config_file = __get_environment_file(config_path=env_path, main_file=main_file, local_file=local_file)
		load_config = __load_configuration_file(config_file=config_file)

		if load_config:
			os.environ[NameConst.ENV_LOAD_STATUS_KEY_NAME] = '1'
		else:
			raise MsbConfigException.ConfigurationLoadingFailed(config_file)
	except Exception as e:
		logging.error(e)
		exit()
