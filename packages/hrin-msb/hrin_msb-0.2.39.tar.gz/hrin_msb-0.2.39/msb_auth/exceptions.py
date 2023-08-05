from msb_exceptions import ApiException


class MsbAuthExceptions:
	class AuthenticationFailed(ApiException):
		"""
			general exception that user needs to see
		"""
		_message = "Authentication failed."
		_code = 640

	class InvalidRequestParameters(ApiException):
		"""
		If failed to build the auth data
		"""
		_message = "Invalid request parameters."
		_code = 641

	class InvalidTokenOwner(ApiException):
		_message = "Token Owner has changed."
		_code = 641

	class InvalidTokenEnvironment(ApiException):
		_message = "Access token belongs to another environment."
		_code = 641

	class InvalidSubscriptionAccess(ApiException):
		_message = "You are not subscribed to this service."
		_code = 641

	class UnauthorizedAccess(ApiException):
		_message = "Unauthorized Access."
		_code = 641
