from msb.exceptions import AppException


class CipherExceptions:
	class NoneValue(AppException):
		_message = "Input value shouldn't be of 'None' type."
