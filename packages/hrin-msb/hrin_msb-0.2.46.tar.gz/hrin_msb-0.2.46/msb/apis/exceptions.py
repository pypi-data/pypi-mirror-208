from msb.exceptions import ApiException


class ApiViewExceptions:
	class UserAuthenticationFailed(ApiException):
		_message = "Failed to authenticate user details."

	class InvalidUserAuthorizationDetails(ApiException):
		_message = "User authorization details not provided."


class ApiViewsetExceptions:
	class SchemaValidationClassNotDefined(ApiException):
		_message = "Api class inherited from 'ApiViewset' must have a 'validation_schema_class' property defined." \
		           "The value of which should be the class which holds your validation rules."
