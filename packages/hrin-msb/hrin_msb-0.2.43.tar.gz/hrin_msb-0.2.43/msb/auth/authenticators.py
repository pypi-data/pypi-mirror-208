from rest_framework.request import Request

from .constants import AUTH_REQUEST_USER_FIELD_NAME, AUTH_REQUEST_PASSWORD_FIELD_NAME
from .results import AuthResult


class MsbAuthenticator:
	_config: object = None
	__auth_request: Request = None

	@property
	def auth_request(self) -> Request:
		return self.__auth_request

	@property
	def auth_user(self):
		return self.auth_request.data.get(AUTH_REQUEST_USER_FIELD_NAME, None)

	@property
	def auth_user_password(self):
		return self.auth_request.data.get(AUTH_REQUEST_PASSWORD_FIELD_NAME, None)

	def __init__(self, user: str, pwd: str, request: Request = None):
		self.__auth_request = request

	def authenticate(self, encoded_pwd: str, **kwargs) -> AuthResult:
		raise NotImplementedError
