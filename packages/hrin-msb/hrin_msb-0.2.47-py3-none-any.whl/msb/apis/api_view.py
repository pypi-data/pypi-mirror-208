from typing import Union

from django.db.models import QuerySet
from msb.auth import (TokenUser, SessionData, Permissions)
from msb.cipher import Cipher
from msb.http import (ApiResponse, RequestInfo, RequestHeaders)
from rest_framework import (viewsets, serializers, exceptions as drf_exceptions)

from .constants import DEFAULT_LOGGER_NAME


def api_details(request=None, ver='', name=''):
	return ApiResponse.success(
		data=dict(method=request.method, version=ver, name=name)
	)


class ApiView(viewsets.GenericViewSet):
	permission_classes = (Permissions.Authenticated,)
	serializer_class = serializers.Serializer
	default_logger: str = DEFAULT_LOGGER_NAME

	@property
	def cipher(self) -> Cipher:
		return Cipher

	@property
	def exceptions(self):
		return drf_exceptions

	def handle_exception(self, exc):
		"""
		override parent exception handler, to send custom error messages as a response
		"""
		try:
			_auth_exceptions = (self.exceptions.NotAuthenticated, self.exceptions.AuthenticationFailed)
			if isinstance(exc, _auth_exceptions):
				if (auth_header := self.get_authenticate_header(self.request)) is not None:
					return self.api_response.authentication_failed()
				else:
					return self.api_response.forbidden()

			return self.api_response.formatted_error_response(super().handle_exception(exc=exc))
		except Exception as e:
			return self.api_response.exception(e)

	def api_not_found(self, request, *args, **kwargs):
		return self.api_response.not_found()

	@classmethod
	def route(cls, method: str, url: str, action: str):
		return path(url, cls.as_view(actions={method: action}))

	@property
	def request_info(self) -> RequestInfo:
		return RequestInfo(meta=self.request.META)

	@property
	def request_headers(self) -> RequestHeaders:
		return RequestHeaders(headers=self.request.headers)

	@property
	def user(self) -> TokenUser:
		return self.request.user

	@property
	def session(self) -> SessionData:
		return self.user.session

	@property
	def payload(self) -> dict | list:
		return self.request.data if type(self.request.data) in [list, dict] else {}

	@property
	def params(self) -> dict:
		return self.request.query_params.dict()

	@property
	def logger(self):
		import logging
		return logging.getLogger(self.default_logger)

	@property
	def api_response(self):
		return ApiResponse

	def serializer(self, data: list | dict | QuerySet = None) -> Union[list, dict]:
		if isinstance(data, dict):
			return data

		return (
			[item.dict() if hasattr(item, 'dict') else item for item in data]
		) if (type(data) in [list, QuerySet]) else []
