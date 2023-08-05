from msb_exceptions import AppException


class FileExceptions:
	class DefaultException(AppException):
		_message = "Something went wrong"

	class PdfException(AppException):
		_message = "PDF Error!"

	class CsvException(AppException):
		_message = "Csv Error!"

	class DocxException(AppException):
		_message = "Word File Error!"

	class PdfExistsException(AppException):
		_message = "PDF File Already Exists!"

	class CsvExistsException(AppException):
		_message = "Csv File Already Exists!"

	class DocxExistsException(AppException):
		_message = "Word File Already Exists!"
