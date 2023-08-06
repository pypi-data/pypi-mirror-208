class AppException(Exception):
	_message: str = ''
	_description: str = ''
	_errors: list = []
	_code: int = 600

	def __init__(self, message: str = None, desc: str = None, errors: list = None):
		self._description = f"\nDesc :{desc}" if isinstance(desc, str) else ""
		self._message = message if isinstance(message, str) else self._message
		super().__init__(f"{self._message}{self._description}")
		self._errors = errors if isinstance(errors, dict) else list()

	@property
	def message(self):
		return self._message

	@property
	def description(self):
		return self._description

	@property
	def errors(self):
		return self._errors

	@property
	def code(self):
		return self._code

	def log(self):
		import logging
		logging.exception(self)


class ApiException(AppException):
	def __init__(self, message: str = None, desc: str = None, errors: dict = None):
		super().__init__(message=message, errors=errors, desc=desc)


class CrudApiException(ApiException):
	_message: str = "Failed to process the {resource} data."

	def __init__(self, resource: str, desc: str = None, errors: dict = None):
		message = self._message.format(resource=(resource or "requested"))
		super().__init__(message=message, errors=errors, desc=desc)
