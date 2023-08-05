from msb_exceptions import CrudApiException


class ApiServiceExceptions:
	class InvalidDatabaseModel(CrudApiException):
		_message = "Invalid database model for {resource} in services."

	class InvalidPk(CrudApiException):
		_message = "Primary Identifier Field for {resource} can't be empty."

	class InvalidDataForCreateOperation(CrudApiException):
		_message = "Invalid data for {resource} creation."

	class CreateOperationFailed(CrudApiException):
		_message = "Failed to create {resource}."

	class RetrieveOperationFailed(CrudApiException):
		_message = "Failed to retrieve {resource} details."

	class ResourseDoesNotExists(CrudApiException):
		_message = "Requested {resource} does not exist."

	class ListOperationFailed(CrudApiException):
		_message = "Failed to retrieve {resource} list."

	class UpdateOperationFailed(CrudApiException):
		_message = "Failed to update {resource}."

	class BulkUpdateOperationFailed(CrudApiException):
		_message = "Failed to update {resource} in bulk."

	class DeleteOperationFailed(CrudApiException):
		_message = "Failed to delete {resource}."

	class BulkDeleteOperationFailed(CrudApiException):
		_message = "Failed to delete {resource} in bulk."
