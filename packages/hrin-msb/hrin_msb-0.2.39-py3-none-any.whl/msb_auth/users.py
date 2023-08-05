from django.utils.functional import cached_property

from .token import AuthToken


class TokenUser(AuthToken):

	@cached_property
	def username(self):
		return self.session.get('username', None)

	@property
	def is_authenticated(self):
		return self.session.get('is_authenticated', False) and self.is_valid

	@cached_property
	def is_admin(self):
		return self.session.get("is_admin") == True

	@property
	def email(self):
		return self.session.get(self._user_email_field)

	def has_access_to(self, path: str):
		return path in self.session.subscriptions
