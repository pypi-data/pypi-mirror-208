from os import environ

from rest_framework.test import APILiveServerTestCase

from .core import (TestConfig, LiveServerThreadWithReuse, const)


class ApiTestResult:
	data = None
	message: str = ''
	code: int = 0
	success: bool = False

	def __init__(self, success=None, code=None, message='', data=None, **kwargs):
		self.data = data if data is not None else []
		self.message = message
		self.code = code
		self.success = success

	@property
	def dict(self):
		return self.__dict__


class ApiTestConfig(TestConfig):

	@property
	def base_url(self):
		return self.get('BASE_URL', default=environ.get('BASE_URL', default='')).rstrip('/')

	def make_url(self, endpoint: str = ''):
		return f"{self.base_url}/{endpoint.replace('.', '/')}"

	@property
	def default_headers(self):
		_headers = {
			const.CONTENT_TYPE_FIELD: const.CONTENT_TYPE_JSON
		}
		if self.user_agent:
			_headers[const.USER_AGENT_FIELD_NAME] = self.user_agent

		return _headers

	@property
	def user_agent(self):
		return self.get(const.CONFIG_USER_AGENT_NAME, default=const.DEFAULT_USER_AGENT)

	@property
	def auth_url(self):
		return self.get(const.CONFIG_AUTH_ENDPOINT, default='')


class ApiTest(APILiveServerTestCase, ApiTestConfig):
	databases = const.DEFAULT_TEST_DATABASES
	port = const.DEFAULT_TEST_SERVER_PORT
	server_thread_class = LiveServerThreadWithReuse

	__auth_tokens: dict = dict()
	_api_endpoints: dict = {}

	def __init__(self, *args, **kwargs):
		APILiveServerTestCase.__init__(self, *args, **kwargs)
		ApiTestConfig.__init__(self)

	def url(self, name: str):
		return self._api_endpoints.get(name)

	def setUp(self) -> None:
		self._authenticate(self.auth_credentials)

	@property
	def access_token(self):
		return self.__auth_tokens.get(const.ACCESS_TOKEN_NAME)

	@property
	def is_authenticated(self):
		return self.access_token not in ['', None]

	@property
	def api_test_result(self):
		return ApiTestResult

	def __log_api_request(self, **kwargs):
		if environ.get('ENVIRONMENT') == 'local':
			logstr = "{sep}Request: {method} {url}\nPayload: {data}\nOptions: {opt}\nResponse: {result}\n{sep}".format(
				sep=f"{'=' * 100}\n", method=kwargs.get('method').upper(), url=kwargs.get('request_url'),
				data=kwargs.get('data'), result=kwargs.get('response'), opt=kwargs.get('opt')
			)
			print(logstr)

	def __make_api_request(self, method='post', endpoint: str = '', data: dict | list = None, _func=None,
	                       **opt) -> ApiTestResult:
		data = dict() if data is None else data
		result = dict()
		try:
			extra_headers = opt.get('headers') if isinstance(opt.get('headers'), dict) else {}
			request_headers = {**self.default_headers, **extra_headers}
			request_url = self.make_url(endpoint=endpoint)

			if self.access_token:
				self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

			handler_func = _func if callable(_func) else self.client.post
			api_response = handler_func(request_url, data, 'json', **request_headers)

			if api_response.headers.get(const.CONTENT_TYPE_FIELD) == const.CONTENT_TYPE_JSON:
				result = api_response.json()
			else:
				result = dict(body=api_response.getvalue())
		except Exception as e:
			pass
		finally:
			self.__log_api_request(method=method, request_url=request_url, data=data, opt=opt, response=result)
			result = ApiTestResult(**result)

		# return only the data section of the api response, unless specifically asked for
		return result

	def _authenticate(self, auth_credentials: dict | list = None) -> None:
		if self.is_authenticated:
			return
		auth_result = self.api_post(self.auth_url, payload=auth_credentials)
		if self.assertEquals(list(auth_result.data.keys()), [const.REFRESH_TOKEN_NAME, const.ACCESS_TOKEN_NAME]):
			self.__auth_tokens = dict(auth_result.data)

	def api_get(self, endpoint: str = '', payload: dict | list = None, **opt) -> ApiTestResult:
		return self.__make_api_request('get', endpoint, payload, _func=self.client.get, **opt)

	def api_post(self, endpoint: str = '', payload: dict | list = None, **opt) -> ApiTestResult:
		return self.__make_api_request('post', endpoint, payload, _func=self.client.post, **opt)

	def api_put(self, endpoint: str = '', payload: dict | list = None, **opt) -> ApiTestResult:
		return self.__make_api_request('put', endpoint, payload, _func=self.client.put, **opt)

	def api_delete(self, endpoint: str = '', payload: dict = None, **opt) -> ApiTestResult:
		return self.__make_api_request('delete', endpoint, payload, _func=self.client.delete, **opt)
