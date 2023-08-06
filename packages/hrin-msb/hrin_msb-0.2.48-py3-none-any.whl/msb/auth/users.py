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
		return (self.session.get("is_admin") == True) and self.has_management_access

	@property
	def email(self):
		return self.session.get('email', None)

	@property
	def has_management_access(self) -> bool:
		return self.session.has_management_access

	@property
	def work_id(self) -> str:
		return self.session.work_id

	@property
	def image(self) -> str:
		return self.session.image

	@property
	def permissions(self) -> dict:
		return self.session.permissions

	@property
	def login_time(self):
		return self.session.login_time

	@property
	def location(self):
		return self.session.location

	@property
	def role(self):
		return self.session.role

	@property
	def subscriptions(self):
		return self.session.subscriptions

	@property
	def dr_list(self):
		return self.session.dr_list

	def has_access_to(self, path: str) -> bool:
		return path in self.session.subscriptions

	def can_manage(self, userid) -> bool:
		return userid in self.dr_list

	def has_role(self, role) -> bool:
		return int(role) == (self.role.id)
