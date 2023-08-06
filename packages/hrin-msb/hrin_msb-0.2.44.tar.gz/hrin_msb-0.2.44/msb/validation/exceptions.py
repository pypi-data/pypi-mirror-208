from msb.exceptions import AppException


class ValidationExceptions:
	class InvalidValidationSchema(AppException):
		_message = 'Validation schema should be of type ValidationSchema.'

	class InvalidValidationInput(AppException):
		_message = 'Validation input should be of type dict or list.'

	class SchemaValidationFailed(AppException):
		_message = 'Failed to validate the input against the given schema.'

	class ErrorFormattingFailed(AppException):
		_message = 'Failed to format the validation errors.'

	class ValidationFailed(AppException):
		_message = 'Failed to validate the request data.'

	class InvalidPayloadException(AppException):
		_message = 'Invalid payload recieved.'

	class InvalidParamsException(AppException):
		_message = 'Invalid request parameters recieved.'

	class InvalidPayloadFormat(AppException):
		_message = 'Malformed request data recieved.'








__all__ = ["ValidationExceptions"]
