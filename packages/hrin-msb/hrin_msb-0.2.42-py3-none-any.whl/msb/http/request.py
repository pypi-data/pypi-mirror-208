from __future__ import annotations


class RequestInfo:
	__request_info = None

	def __init__(self, meta=None):
		self.__request_info = meta

	def get(self, key: str = None, default=None):
		val = self.__request_info.get(key)
		return val if val is not None else default

	@property
	def cookie(self):
		return self.__request_info.get('HTTP_COOKIE')

	@property
	def path(self) -> str:
		return self.__request_info.get('PATH_INFO')

	@property
	def ip(self):
		return self.__request_info.get('REMOTE_ADDR')

	@property
	def method(self) -> str:
		return self.__request_info.get('REQUEST_METHOD')

	@property
	def script(self) -> str:
		return self.__request_info.get('SCRIPT_NAME')

	@property
	def server(self) -> str:
		return self.__request_info.get('SERVER_NAME')

	@property
	def port(self) -> int:
		return int(self.__request_info.get('SERVER_PORT'))

	@property
	def protocol(self) -> str:
		return self.__request_info.get('SERVER_PROTOCOL')

	@property
	def content_type(self) -> str:
		return self.__request_info.get('CONTENT_TYPE')

	@property
	def query_string(self) -> str:
		return self.__request_info.get('QUERY_STRING')

	@property
	def authorization(self) -> str:
		return self.__request_info.get('HTTP_AUTHORIZATION')


class RequestHeaders:
	__headers = None

	def __init__(self, headers=None):
		self.__headers = headers

	@property
	def user_agent(self) -> str:
		return self.__headers.get('User-Agent')
