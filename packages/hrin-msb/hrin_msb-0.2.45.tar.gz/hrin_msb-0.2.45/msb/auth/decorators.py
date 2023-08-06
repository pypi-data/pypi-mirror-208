from functools import wraps

from .exceptions import MsbAuthExceptions


def api_permissions(*permission_classes, _all: bool = False):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request, *args, **kwargs):
			evaluator = all if _all else any

			if not evaluator([permission().has_permission(request, cls) for permission in permission_classes]):
				raise MsbAuthExceptions.UnauthorizedAccess

			return _decorated_function(cls, *args, **dict(request=request, **kwargs))

		return wrapper_function

	return decorator_function


def require_role(*role_ids):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request, *args, **kwargs):
			if not any([request.user.has_role(role_id) for role_id in role_ids]):
				raise MsbAuthExceptions.UnauthorizedAccess

			return _decorated_function(cls, *args, **dict(request=request, **kwargs))

		return wrapper_function

	return decorator_function
