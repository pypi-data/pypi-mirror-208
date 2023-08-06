from functools import wraps

from .exceptions import MsbAuthExceptions


def api_permissions(*permission_classes, _all: bool = False,**kwargs):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request, *args, **kwargs):
			override_validation = kwargs.get('override',True)
			api_permission_is_validated = getattr(cls,'_api_permission_is_validated',False)

			if override_validation and not api_permission_is_validated:
				evaluator = all if _all else any
				if not evaluator([permission().has_permission(request, cls) for permission in permission_classes]):
					raise MsbAuthExceptions.UnauthorizedAccess
				cls._api_permission_is_validated = True
			return _decorated_function(cls, *args, **dict(request=request, **kwargs))

		return wrapper_function

	return decorator_function


def require_role(*role_ids):
	def decorator_function(_decorated_function):
		@wraps(_decorated_function)
		def wrapper_function(cls, request, *args, **kwargs):
			if not any([request.user.has_role(role_id) for role_id in role_ids]):
				raise MsbAuthExceptions.UnauthorizedAccess

			_kwargs = dict(request=request, **kwargs)
			return _decorated_function(cls, *args, **_kwargs)

		return wrapper_function

	return decorator_function


