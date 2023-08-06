import json
from typing import (List, Dict)

from requests import (api, ConnectionError,Timeout)
from requests.models import Response

from .constants import (HttpHeaders, HttpContentType)
from .dataclasses import (RestRequest, ApiResponseWrapper)
from .exceptions import ApiRequestExceptions

"""
Contains all the parameters required to make a request to the API.
"""


class ApiRequestParameter:

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
		return self.headers.get(HttpHeaders.CONTENT_TYPE) == HttpContentType.APPLICATION_JSON

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
				_query_params = f"/{'/'.join([str(i) for i in params])}"
		self.query_params = _query_params
		return self

	def set_cookies(self, cookies):
		self.cookies = cookies
		return self

	def set_request_method(self, method: str):
		self.method = method
		return self

	def set_authorization(self, token: str):
		self.add_header(HttpHeaders.AUTHORIZATION, HttpHeaders.BEARER_TOKEN_VALUE.format(token=token))
		return self

	def set_verify_ssl(self, verify: bool):
		self.verify_ssl = verify

	def __init__(self, api_host: str = '', **kwargs):
		self.headers = {HttpHeaders.CONTENT_TYPE: HttpContentType.APPLICATION_JSON}
		self.cookies = None
		self.set_request_method(None)
		self.set_api_host(api_host)
		self.set_endpoint("")
		self.set_query_params([])
		self.set_data({})
		self.set_verify_ssl(kwargs.get('verify_ssl', False))

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return f"ApiRequestParameter(url={self.request_url}, method={self.request_method},data=" \
		       f"{self.request_data}, headers={self.request_headers}, cookies={self.request_cookies},"


"""
Core Api Request class.
"""


class ApiRequestCore(ApiRequestParameter):

	def _execute(self) -> ApiResponseWrapper:
		api_response = Response()
		try:
			request_parameters = self.get_request_parameters()
			api_response = api.request(**request_parameters)
			return ApiResponseWrapper(api_response)
		except ConnectionError as ce:
			raise ApiRequestExceptions.ResourceUnreachable
		except Timeout as te:
			raise ApiRequestExceptions.ResourceNotResponding
		except Exception as e:
			raise ApiRequestExceptions.InternalServerError


	@property
	def request_is_json(self) -> bool:
		return True

	def get_result(self) -> Dict:
		return self._execute().to_json()

	def __str__(self):
		return f"<{self.__class__.__name__}: {self.request_method.upper()} {self.request_url}>"


class ApiRouterClient(ApiRequestCore):

	def __init__(self, request: RestRequest, **kwargs):
		super(ApiRouterClient, self).__init__(**kwargs)
		if kwargs.get('clone') == True:
			self.set_request_method(request.method)
			self.set_data(request.data)
			self.set_query_params(request.query_params)

		self.headers = request.headers
		self.cookies = request.META.get('HTTP_COOKIE')

	def get_result(self) -> ApiResponseWrapper:
		if not self.request_is_valid:
			raise ApiRequestExceptions.InvalidRequestParameters
		return self._execute()


class ApiRequest(ApiRequestCore):

	def REQUEST(self, method: str, endpoint: str, data: [List | Dict] = None, query_params: [List | Dict] = None, ):
		return self.set_query_params(query_params).set_request_method(method).set_endpoint(endpoint).set_data(data)

	def GET(self, query_params: [List | Dict] = None, endpoint: str = None):
		return self.set_query_params(params=query_params).set_request_method("GET").set_endpoint(endpoint)

	def POST(self, data: [List | Dict] = None, query_params: [List | Dict] = None, endpoint: str = None):
		return self.set_data(data=data).set_query_params(params=query_params).set_request_method("POST").set_endpoint(
			endpoint)

	def PUT(self, data: [List | Dict] = None, query_params: [List | Dict] = None, endpoint: str = None):
		return self.set_data(data=data).set_query_params(params=query_params).set_request_method("PUT").set_endpoint(
			endpoint)

	def DELETE(self, data: [List | Dict] = None, query_params: [List | Dict] = None, endpoint: str = None):
		return self.set_data(data=data).set_query_params(params=query_params).set_request_method("DELETE").set_endpoint(
			endpoint)
