from rest_framework.permissions import BasePermission

from .exceptions import MsbAuthExceptions
from .users import TokenUser


class Permissions:

	class Authenticated(BasePermission):

		def has_permission(self, request, view) -> bool:
			return bool(request.user and request.user.is_authenticated)

		def has_object_permission(self, request, view, obj):
			return True

		def check(self, request, view, obj=None) -> bool:
			if not self.has_permission(request, view, ):
				raise MsbAuthExceptions.UnauthorizedAccess
			return True

	class Admin(Authenticated):
		def has_permission(self, request, view) -> bool:
			return bool(
				super().has_permission(request, view) and
				request.user.is_admin
			)

	class Management(Authenticated):
		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_management_access)

	class IntraService(Authenticated):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(
				super().has_permission(request, view) and _user.is_intra_service_requester)

	class ManagementOrIntraService(Authenticated):
		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(
				super().has_permission(request, view) and
				(_user.has_management_access or _user.is_intra_service_requester)
			)
