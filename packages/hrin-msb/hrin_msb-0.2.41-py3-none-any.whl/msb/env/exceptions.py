from msb.exceptions import AppException


class MsbConfigException():
	class BaseDirDoesNotExists(AppException):
		_message = "Root Directory Does Not Exists."

	class ConfigFileDoesNotExist(AppException):
		_message = "Configuration File Does Not Exists."

	class ConfigurationLoadingFailed(AppException):
		_message = "Failed To Load Configuration From envutil File."
