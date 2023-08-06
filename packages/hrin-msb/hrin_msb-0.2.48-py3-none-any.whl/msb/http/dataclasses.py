from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Union

from requests.models import Response
from rest_framework import request as drf_request
from rest_framework.request import Request as RestRequest
from rest_framework.response import Response as HttpResponse

from msb.dataclasses import Singleton
from msb.env import (Config)
from . import constants as http_const
from .exceptions import ApiRequestExceptions


class HostUrlsConfig(metaclass=Singleton):
	__config_key = "{service_name}_SERVICE_URL"

	def __get_service_host(self, service_name: str):
		_config_name = self.__config_key.format(service_name=service_name.upper())
		return Config.get(_config_name).as_str(default=None)

	def using(self, request_path: str):
		_remote_service_url, *_service_url = (None, [])

		# Separate base service and url from main url
		_service_name, *_service_url = request_path.lstrip("/").split("/")
		_remote_service_url = self.__get_service_host(service_name=_service_name)

		if Config.is_local_env():
			print(f"{_remote_service_url = }")

		return _remote_service_url, "/".join(_service_url)


class ApiRequestData:

	@property
	def _api_host(self):
		return (self.api_host or "").strip("/")

	@property
	def _api_endpoint(self):
		return (self.endpoint or "").strip("/")

	@property
	def request_is_valid(self) -> bool:
		return True

	@property
	def request_is_json(self) -> bool:
		return self.headers.get(http_const.HEADER_NAME_CONTENT_TYPE) == http_const.CONTENT_TYPE_APPLICATION_JSON

	@property
	def request_verify_certificate(self) -> bool:
		return False

	@property
	def request_method(self):
		return self.method

	@property
	def request_headers(self):
		return self.headers

	@property
	def request_query(self):
		return self.query_params

	@property
	def request_url(self):
		_host = self._api_host.strip("/")
		return f"{_host}/{self._api_endpoint}{self.request_query}".strip("/")

	@property
	def request_cookies(self):
		return self.cookies

	@property
	def request_data(self):
		return json.dumps(self.data)

	def get_request_parameters(self):
		_parameters = dict(
			method=self.request_method, url=self.request_url, data=self.request_data,
			verify=self.request_verify_certificate, json=self.request_is_json,
		)

		if self.request_cookies:
			_parameters['cookies'] = self.request_cookies

		if self.request_headers:
			_parameters['headers'] = self.request_headers

		return _parameters

	"""	SETTERS	"""

	def set_endpoint(self, endpoint: str):
		if endpoint:
			self.endpoint = endpoint.rstrip("/")
		return self

	def set_api_host(self, host: str):
		self.api_host = host.rstrip("/") if isinstance(host, str) and len(host) > 0 else None
		return self

	def add_header(self, name: str, value: str):
		self.headers[name] = value
		return self

	def set_data(self, data: [list, dict]):
		self.data = data
		return self

	def set_query_params(self, params: [list, dict]):
		_query_params = ""
		if (params_type := type(params)) in [list, dict]:
			if params_type == dict:
				_query_params = f"""?{"&".join([f"{k}={v}" for k, v in params.items()])}"""
			else:
				_query_params = f"""/{"/".join(params)}"""
		self.query_params = _query_params
		return self

	def set_cookies(self, cookies):
		self.cookies = cookies
		return self

	def set_request_method(self, method: str):
		self.method = method
		return self

	def __init__(self, api_host: str = '', request: RestRequest = None):
		self.method = None
		self.set_api_host(api_host)
		self.set_endpoint("")
		self.set_query_params([])
		self.set_data({})
		self.headers = request.headers if isinstance(request, RestRequest) else dict()
		self.cookies = request.META.get('HTTP_COOKIE') if isinstance(request, RestRequest) else None


class ApiResponseWrapper:
	__response: Response

	@property
	def response(self) -> Response:
		return self.__response

	def __init__(self, response: Response):
		self.__response = response

	def to_json(self) -> dict:
		if self.response.headers.get(http_const.HEADER_NAME_CONTENT_TYPE) == http_const.CONTENT_TYPE_APPLICATION_JSON:
			return self.response.json()

		if self.response.status_code in [404]:
			raise ApiRequestExceptions.ResourceNotFound

	def as_msb_api_response(self) -> MsbApiResponse:
		try:
			return MsbApiResponse(response=self.response)
		except Exception as e:
			return MsbApiResponse(dict())

	def to_http_response(self) -> HttpResponse:
		return HttpResponse(
			data=self.to_json(),
			headers=self.response.headers,
			status=self.response.status_code
		)


class MsbApiResponse:
	__response_body: dict

	def __init__(self, response: Response):
		try:
			self.__response_body = response.json()
		except Exception as e:
			self.__response_body = dict()

	@property
	def code(self):
		return self.__response_body.get("code")

	@property
	def success(self):
		return self.__response_body.get("success") == True

	@property
	def is_valid(self) -> bool:
		return self.success and self.code == 200

	@property
	def data(self):
		_data = self.__response_body.get("data") or []
		return _data

	@property
	def message(self) -> str:
		return self.__response_body.get("message") or "Failure"

	@property
	def body(self) -> str | dict:
		return self.__response_body

	def __str__(self):
		return json.dumps(self.body)


@dataclass
class RequestWrapper:
	request: Union[drf_request.Request] = None

	@property
	def meta(self) -> dict:
		return self.request.META or {}

	@property
	def headers(self) -> dict:
		return self.request.headers or {}

	@property
	def cookie(self):
		return self.meta.get('HTTP_COOKIE')

	@property
	def path(self) -> str:
		return self.meta.get('PATH_INFO')

	@property
	def ip(self):
		return self.headers.get('X-Real-Ip') or self.meta.get('REMOTE_ADDR')

	@property
	def method(self) -> str:
		return self.meta.get('REQUEST_METHOD')

	@property
	def script(self) -> str:
		return self.meta.get('SCRIPT_NAME')

	@property
	def server(self) -> str:
		return self.meta.get('SERVER_NAME')

	@property
	def port(self) -> int:
		return int(self.meta.get('SERVER_PORT'))

	@property
	def protocol(self) -> str:
		return self.meta.get('SERVER_PROTOCOL')

	@property
	def content_type(self) -> str:
		return self.meta.get('CONTENT_TYPE')

	@property
	def query_string(self) -> str:
		return self.meta.get('QUERY_STRING')

	@property
	def authorization(self) -> str:
		return self.meta.get('HTTP_AUTHORIZATION')

	@property
	def user_agent(self) -> str:
		return self.headers.get('User-Agent')

	@property
	def path(self) -> str:
		return self.meta.get('PATH_INFO')
