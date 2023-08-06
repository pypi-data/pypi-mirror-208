from django.utils.functional import cached_property

from msb.cipher import Cipher
from .constants import TokenConst, AUTH_TOKEN_ACCESS_TYPE_ISR, AUTH_REQUEST_TYPE_ISR
from .session import SessionData


class AuthToken:
	token: dict
	_userid_field: str = TokenConst.userid_field

	def __init__(self, tokendata: dict = None):
		self.token = tokendata if tokendata else dict()

	def __str__(self):
		return f"<{self.__class__.__name__} [{self.id}]: {self.username}>"

	def __hash__(self):
		return hash(self.username)

	def __getattr__(self, attr):
		"""This acts as a backup attribute getter for custom claims defined in Token serializers."""
		return self.token.get(attr, None)

	def set_validation_status(self, status: bool = False):
		self.token['is_valid'] = status

	@property
	def owner(self):
		return Cipher.decrypt(self.token.get('owner'))

	@cached_property
	def id(self):
		return self.token.get(self._userid_field)

	@cached_property
	def userid(self):
		return self.id

	@property
	def is_valid(self):
		return self.token.get('is_valid', False)

	@cached_property
	def session(self) -> SessionData:
		session_data = self.token.get('session', {})
		return session_data if isinstance(session_data, SessionData) else SessionData(**session_data)

	@cached_property
	def access_type(self):
		return Cipher.decrypt(self.token.get('access_type'))

	@property
	def env(self):
		return Cipher.decrypt(self.token.get('env'))

	@cached_property
	def auth_type(self) -> str:
		return self.session.get('auth_type', '')

	@property
	def is_intra_service_requester(self):
		return (
			self.access_type.casefold() == AUTH_TOKEN_ACCESS_TYPE_ISR.casefold()
			and self.auth_type.casefold() == AUTH_REQUEST_TYPE_ISR.casefold()
		)
