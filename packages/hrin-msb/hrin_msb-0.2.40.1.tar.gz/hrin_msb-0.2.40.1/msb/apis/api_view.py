from typing import Union

from django.db.models import QuerySet
from rest_framework import (viewsets, serializers, exceptions)

from msb.auth import permissions
from msb.auth.session import SessionData
from msb.auth.users import TokenUser
from msb.http import (ApiResponse, RequestInfo, RequestHeaders)
from .constants import DEFAULT_LOGGER_NAME


def api_details(request=None, ver='', name=''):
	return ApiResponse.success(
		data=dict(method=request.method, version=ver, name=name)
	)


class ApiView(viewsets.GenericViewSet):
	permission_classes = (permissions.LoginRequiredPermission,)
	serializer_class = serializers.Serializer
	default_logger: str = DEFAULT_LOGGER_NAME

	def handle_exception(self, exc):
		"""
		override parent exception handler, to send custom error messages as a response
		"""
		try:
			_auth_exceptions = (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)
			if isinstance(exc, _auth_exceptions):
				if (auth_header := self.get_authenticate_header(self.request)) is not None:
					return self.api_response.authentication_failed()
				else:
					return self.api_response.forbidden()

			return self.api_response.formatted_error_response(super().handle_exception(exc=exc))
		except Exception as e:
			return self.api_response.exception(e)

	@property
	def request_info(self) -> RequestInfo:
		return RequestInfo(meta=self.request.META)

	@property
	def request_headers(self) -> RequestHeaders:
		return RequestHeaders(headers=self.request.headers)

	@property
	def token(self) -> TokenUser:
		return self.request.user

	@property
	def user(self) -> SessionData:
		return self.token.session

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


class IntraServiceRequestApi(ApiView):
	permission_classes = (permissions.IntraServiceRequestPermission,)
