from msb.exceptions import (ApiException)


class HttpExceptions:
	"""
	list of exceptions related to the api_gateway app
	"""

	class ResourceUnreachable(ApiException):
		_message = "Requested resource is unreachable."
		_code = 500


class ApiRequestExceptions:
	class ResourceNotFound(ApiException):
		"""
			If the requested service is not found.
		"""
		_message = "Requested resource not found."
		_code = 404

	class ResourceUnreachable(ApiException):
		_message = "Requested resource is unreachable."
		_code = 405

	class ResourceNotResponding(ApiException):
		_message = "Requested resource did not respond."
		_code = 405

	class InternalServerError(ApiException):
		_message = "Internal Server Error."
		_code = 500

	class InvalidRequestParameters(ApiException):
		_message = "Invalid request parameters for the request."
		_code = 500

	class InvalidHostOrRequestPath(ApiException):
		_message = "Invalid host or path."
		_code = 500
