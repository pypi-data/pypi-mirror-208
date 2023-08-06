from rest_framework.permissions import BasePermission

from .exceptions import MsbAuthExceptions
from .users import TokenUser
from .constants import RoleConst

class Permissions:
	"""
		Default Permissions
	"""
	class Authenticated(BasePermission):

		def has_permission(self, request, view) -> bool:
			return bool(request.user and request.user.is_authenticated)

		def has_object_permission(self, request, view, obj):
			return True

		def check(self, request, view, obj=None) -> bool:
			if not self.has_permission(request, view, ):
				raise MsbAuthExceptions.UnauthorizedAccess
			return True

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

	"""
		Role Permissions
	"""

	class AdminRole(Management):
		def has_permission(self, request, view) -> bool:
			return bool(super().has_permission(request, view) and request.user.is_admin)

	class ManagerRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.MANAGER_ROLE_ID))

	class EmployeeRole(Authenticated):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.EMPLOYEE_ROLE_ID))

	class HrManagerRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.HR_MANAGER_ROLE_ID))

	class HrEmployeeRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.HR_EMPLOYEE_ROLE_ID))

	class ResourceManagerRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.RESOURCE_MANAGER_ROLE_ID))

	class FinanceManagerRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.FINANCE_MANAGER_ROLE_ID))

	class FinanceEmployeeRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.FINANCE_EMPLOYEE_ROLE_ID))

	class OperationsManagerRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.OPERATIONS_MANAGER_ROLE_ID))

	class OperationsEmployeeRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.OPERATIONS_EMPLOYEE_ROLE_ID))

	class ItManagerRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.IT_MANAGER_ROLE_ID))

	class ItEmployeeRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.IT_EMPLOYEE_ROLE_ID))

	class GuestRole(Authenticated):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.GUEST_ROLE_ID))

	class ContractorRole(Authenticated):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.CONTRACTOR_ROLE_ID))

	class ApplicationQaRole(Management):

		def has_permission(self, request, view) -> bool:
			_user: TokenUser = request.user
			return bool(super().has_permission(request, view) and _user.has_role(RoleConst.APPLICATION_QA_ROLE_ID))