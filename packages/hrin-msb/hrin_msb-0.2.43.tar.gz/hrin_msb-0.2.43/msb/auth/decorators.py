from functools import wraps

from .exceptions import MsbAuthExceptions


def require_permissions(*permission_classes, _any: bool = False):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request, *args, **kwargs):
			evaluator = any if _any else all

			if not evaluator([permission().has_permission(request, cls) for permission in permission_classes]):
				raise MsbAuthExceptions.UnauthorizedAccess

			return _decorated_function(cls, *args, **dict(request=request, **kwargs))

		return wrapper_function

	return decorator_function
