from __future__ import annotations

from msb.exceptions import AppException
from msb.exceptions import MsbExceptionHandler
from rest_framework import status
from rest_framework.response import Response as RestResponse


class ApiResponse:
	data_types = [list, dict]

	@staticmethod
	def _dispatch(data: dict = None, status=status.HTTP_200_OK) -> RestResponse:
		headers = dict()
		_response = RestResponse(data=data, headers=headers, status=status)
		return _response

	@staticmethod
	def success(data=None, msg: str = 'ok') -> RestResponse:
		response_data = dict(
			success=True, message=msg,
			code=200, data=([] if type(data) not in ApiResponse.data_types else data)
		)
		return ApiResponse._dispatch(data=response_data)

	@staticmethod
	def error(msg: str = "Failure", err_code=600, data=None, http_code=status.HTTP_200_OK) -> RestResponse:
		response_data = dict(
			success=False,
			message=msg,
			code=err_code,
			data=([] if type(data) not in ApiResponse.data_types else data)
		)
		return ApiResponse._dispatch(data=response_data, status=http_code)

	@staticmethod
	def exception(e: AppException | Exception = None, fallback: bool = True) -> RestResponse:
		MsbExceptionHandler.handle_exception(e=e)
		if not isinstance(e, AppException):
			return ApiResponse.internal_server_error()

		return ApiResponse.error(
			msg=e.message if hasattr(e, 'message') else str(e),
			data=e.errors if hasattr(e, 'errors') else [],
			err_code=e.code if hasattr(e, 'code') else 500
		)

	@staticmethod
	def not_found(msg: str = "Resource Not Found.", **kwargs):
		response_data = dict(success=False, message=msg, code=404, data=[])
		return ApiResponse._dispatch(data=response_data, status=status.HTTP_404_NOT_FOUND)

	@staticmethod
	def authentication_failed(msg: str = "Authentication Failed.", **kwargs):
		response_data = dict(success=False, message=msg, code=401, data=[])
		return ApiResponse._dispatch(data=response_data, status=status.HTTP_401_UNAUTHORIZED)

	@staticmethod
	def forbidden(msg: str = "Access Forbidden.", **kwargs):
		response_data = dict(success=False, message=msg, code=403, data=[])
		return ApiResponse._dispatch(data=response_data, status=status.HTTP_403_FORBIDDEN)

	@staticmethod
	def bad_request(msg: str = "Bad Request.", **kwargs):
		response_data = dict(success=False, message=msg, code=400, data=[])
		return ApiResponse._dispatch(data=response_data, status=status.HTTP_400_BAD_REQUEST)

	@staticmethod
	def method_not_allowed(msg: str = "Method Not Allowed.", **kwargs):
		response_data = dict(success=False, message=msg, code=405, data=[])
		return ApiResponse._dispatch(data=response_data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

	@staticmethod
	def internal_server_error(msg: str = "Internal Server Error", **kwargs):
		response_data = dict(success=False, message=msg, code=500, data=[])
		return ApiResponse._dispatch(
			data=response_data,
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)

	@staticmethod
	def formatted_error_response(response: RestResponse) -> RestResponse:
		_code = response.status_code or None
		_message = response.data.get('detail') or None
		if _code is not None and _message is not None:
			return ApiResponse.error(err_code=_code, msg=_message.replace('"', "'"), http_code=_code)
		return ApiResponse.internal_server_error()
