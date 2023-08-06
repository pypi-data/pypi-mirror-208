from rest_framework.permissions import BasePermission


class MsbPermisson(BasePermission):

	def has_permission(self, request, view):
		return True

	def has_object_permission(self, request, view, obj):
		return True


class LoginRequiredPermission(MsbPermisson):

	def has_permission(self, request, view):
		return bool(request.user and request.user.is_authenticated)


class AdminUserPermission(MsbPermisson):
	def has_permission(self, request, view):
		return bool(request.user and request.user.is_staff)


class IntraServiceRequestPermission(LoginRequiredPermission):

	def has_permission(self, request, view) -> bool:
		if super().has_permission(request, view):
			return request.user.is_intra_service_requester
		return False
